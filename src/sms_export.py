import asyncio
import json
import logging
import time
from collections import defaultdict
from datetime import datetime
from typing import Type, List

from models.messages_models import CompositeSMS
from repositories.pg_repository import PostgresRepository
from repositories.telegram_alerting import TelegramAlerting
from settings import Settings, config


class SMSExporter:

    def __init__(self, logger, pg_repo: Type[PostgresRepository], config: Settings, alerting: Type[TelegramAlerting]):
        self.config = config
        self.logger = logger
        self.name = config.app_modem_name
        self.alerting = alerting(config, logger)
        self.pg_conn = pg_repo(config)
        self.chat_id = None
        self.top_id = None

    def get_workflow(self):
        sql = f"select * from service.workflow where service_id = '{self.name}'"
        result = self.pg_conn.read_sql(sql)
        if not result:
            self.logger.warnig(
                f'External service id not specified (chat id) in workflow table for service_id={self.name}'
            )
            return

        self.chat_id = result[2]
        self.top_id = int(result[3])

        self.alerting.chat_id = self.chat_id


    def get_latest_sms(self):
        raw_messages = self.pg_conn.read_messages(top_id=self.top_id, name=self.name)
        if not raw_messages:
            return

        without_reference_id = 1
        sms_groups = defaultdict(list)
        for msg in raw_messages:
            if msg.partial is not None:
                    partial = json.loads(msg.partial)
                    msg.part_reference = partial['reference']
                    msg.part_number = partial['part_number']
                    msg.part_count = partial['parts_count']

            if not msg.part_reference:
                sms_groups[without_reference_id].append(msg)
                without_reference_id += 1
            else:
                sms_groups[msg.part_reference].append(msg)

        composite_sms = []

        for group in sms_groups.values():
            if len(group) > 1:
                group.sort(key=lambda x: x.part_number)
            f_elem = group[0]
            c_sms = CompositeSMS(
                sender=f_elem.sender,
                contents=group,
                date=f_elem.received_date,
                parts_total=f_elem.part_count,
            )
            c_sms.check()

            if c_sms.is_completed:
                composite_sms.append(c_sms)
                # current_max_id = max(x.id for x in group)
                pass

        composite_sms = []
        for group in sms_groups.values():
            f_elem = group[0]

            c_sms = CompositeSMS(
                        sender=f_elem.sender,
                        contents=group,
                        date=f_elem.received_date,
                        parts_total=f_elem.part_count,
                    )

            c_sms.check()

            if c_sms.is_completed:
                composite_sms.append(c_sms)

        composite_sms.sort(key=lambda x: x.max_id)
        return composite_sms

    def set_max_id(self):
        sql = f"update service.workflow set top_id = {self.top_id} where service_id = '{self.name}'"
        self.pg_conn.execute_sql(sql)

    def export(self, sms_to_export: List[CompositeSMS]):

        for sms in sms_to_export:
            msg = (
                f'Вам *СМС* \n'
                f'*От*: {sms.sender} \n'
                f'{sms.full_text} \n'
                f'*Время*: {sms.received_date} \n'
                f'*Сервис*: {sms.service_id}'
            )

            result = asyncio.run(self.alerting.send(msg))
            if not result or result != 200:
                for i  in range(10):
                    time.sleep(1)
                    result = asyncio.run(self.alerting.send(msg))
                    if result:
                        break
            time.sleep(0.5)
            if self.top_id < sms.max_id:
                self.top_id = sms.max_id
                self.set_max_id()
            self.logger.info(f'Sent SMS top_id {self.top_id}')


    def run_pipeline(self):
        self.get_workflow()
        cnt = 1
        while True:
            s_time = datetime.now().second
            if s_time % 10 == 0:
                sms_to_export = self.get_latest_sms()
                if sms_to_export:
                    self.export(sms_to_export)

            time.sleep(1)
            cnt += 1
            if cnt >= 600:
                self.logger.info('Waiting SMS to export ...')
                cnt = 0



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger('SMSExporter')

    exporter = SMSExporter(log, PostgresRepository, config, TelegramAlerting)
    exporter.run_pipeline()
