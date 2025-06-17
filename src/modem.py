import asyncio
import logging
import signal
import time
from datetime import datetime
from typing import List, Type

import serial
from smspdudecoder.easy import read_incoming_sms

from config_loader import ExtraConfig
from models.messages_models import SMSMessage
from repositories.saver import BaseSMSRepository, PostgresSaverRepository
from settings import Settings, config


class ModemGSM:
    """
    HUAWEI E1750 SMS Reader
    """
    received: List[SMSMessage]

    def __init__(self, tty_name: str, logger, sms_saver: Type[BaseSMSRepository], config: Settings):
        self.config = config
        self.logger = logger
        self.sms_saver = sms_saver(config)
        self.ser = serial.Serial()
        self.ser.port = tty_name
        self.serial_config()
        self.ser.open()
        self.ser.flush()
        self.poll_interval_sec = 5
        self.post_config()
        self.received = []
        self.logger.info(f'OK! Connected to {self.ser.name}')
        self.CHECK_MINUTES_LIMIT = 43200 // 2  # Two weeks
        self.extra_cfg = ExtraConfig(self.CHECK_MINUTES_LIMIT)
        self.CHECK_MINUTES_LIMIT = self.extra_cfg.min_left
        signal.signal(signal.SIGINT, self.close_connection)
        signal.signal(signal.SIGTERM, self.close_connection)

    def __del__(self):
        self.close_connection()



    def cmd(self, cmd_str):
        cmd_str = (cmd_str + '\r\n').encode('utf-8')
        self.ser.write(cmd_str)

    async def send_control_sms(self):
        # Отправить SMS
        self.cmd(f'AT+CMGS=16')
        await asyncio.sleep(2)
        self.ser.write(self.config.app_control_message_pdu.encode())
        await asyncio.sleep(2)
        self.ser.write(bytes.fromhex('1a'))


    async def get_answer(self):
        while True:
            try:
                line = self.ser.readlines()
            except Exception as e:
                self.logger.error(e)
                break
            if line:
                yield line
            else:
                yield None
                await asyncio.sleep(1.1)

    @staticmethod
    def messages_parser(incomes: list) -> List[SMSMessage]:
        new_input = [x.decode('utf-8').strip('\r\n') for x in incomes if x != b'\r\n']

        sms = []
        for pos, row in enumerate(new_input):
            if '+CMGL:' in row:
                message = read_incoming_sms(new_input[pos + 1])
                sms.append(SMSMessage(**message))

        return sms

    def truncate_modem_sms(self):
        self.cmd('AT+CMGD=2,1')
        self.logger.info('Truncating modem SMS messages')

    def message_income_processing(self, messages: List):
        possible_messages = self.messages_parser(messages)
        if not possible_messages:
            return
        # Try to save SMS to external origin and truncate modem store
        self.sms_saver.save_messages(incoming_messages=possible_messages)
        self.received.extend(possible_messages)
        self.truncate_modem_sms()

    async def cycle_sms_get(self):
        cached_income = None
        start_minute = datetime.now().minute

        async for income in self.get_answer():
            if income is not None:
                if cached_income != income:
                    self.logger.info(income)
                    cached_income = income
                self.message_income_processing(income)

            ts = datetime.now().second
            current_minute = datetime.now().minute
            if ts % self.poll_interval_sec == 0:
                self.logger.debug('send command AT')
                self.cmd('AT+CMGL=4')  # Read all SMS
            if current_minute != start_minute:
                self.logger.info(f'Received messages: {len(self.received)}.'
                                 f' {self.extra_cfg.min_left} minutes left to send control SMS.'
                                 f' Waiting for new messages...')
                start_minute = current_minute
                self.extra_cfg.decrease()
                if self.extra_cfg.min_left <= 0:
                    await self.send_control_sms()
                    self.extra_cfg.reset()

    def serial_config(self):
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 0  # Non-Block reading
        self.ser.xonxoff = False  # Disable Software Flow Control
        self.ser.rtscts = False  # Disable (RTS/CTS) flow Control
        self.ser.dsrdtr = False  # Disable (DSR/DTR) flow Control
        self.ser.writeTimeout = 2
        # self.received = self.sms_saver.get_messages()

    def post_config(self):
        self.cmd('AT+CPMS="MT"')
        self.cmd('AT+CSCS="GSM"')
        self.cmd('AT+CMGF=0')

    def close_connection(self, *args):
        if self.ser.is_open:
            self.logger.debug('Closing serial connection ...')
            self.ser.close()
            self.logger.debug('Connection closed')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger('Modem')

    modem = ModemGSM(tty_name='/dev/ttyUSB0', logger=log, sms_saver=PostgresSaverRepository, config=config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(modem.cycle_sms_get())
