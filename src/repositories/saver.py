import csv
from typing import List

import psycopg2

from models.messages_models import SMSMessage
from settings import Settings


class BaseSMSRepository:

    def __init__(self, config = None):
        pass

    def save_messages(self, **kwargs):
        raise NotImplementedError

    def get_messages(self, **kwargs):
        raise NotImplementedError


class CSVSaverRepository(BaseSMSRepository):
    def __init__(self):
        super().__init__()
        self.path = '/tmp/sms.csv'

    def save_messages(self, incoming_messages: List[SMSMessage]):
        if not incoming_messages:
            return
        fieldnames = ['sender', 'content', 'received_date', 'partial', 'service_id']
        with open(self.path, 'a', newline='') as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            if fp.tell() == 0:
                writer.writeheader()
            for msg in incoming_messages:
                writer.writerow(msg.dict())

    def get_messages(self):
        messages = []
        try:
            with open(self.path, 'r+') as fp:
                reader = csv.DictReader(fp)
                for row in reader:
                    message = SMSMessage(**row)
                    messages.append(message)
        except FileNotFoundError:
            pass
        return messages

class PostgresSaverRepository(BaseSMSRepository):
    def __init__(self, config: Settings):
        super().__init__()
        self.config = config
        self.connection = psycopg2.connect(**self.config.psycopg_dsn)
        self.cur = self.connection.cursor()

    def __del__(self):
        if not self.connection.closed:
            self.cur.close()
            self.connection.close()

    def save_messages(self, incoming_messages: List[SMSMessage]):

        if not incoming_messages:
            return
        sql = '''
        INSERT INTO service.sms_log (sender, content, received_date, partial, service_id)
        VALUES (%(sender)s, %(content)s, %(received_date)s, %(partial)s, %(service_id)s)'''

        self.cur.executemany(sql, [x.dict() for x in incoming_messages])
        self.connection.commit()


    def read_sql(self, sql: str):
        self.cur.execute(sql)
        result = self.cur.fetchone()
        return result

    def execute_sql(self, sql: str):
        self.cur.execute(sql)
        result = self.connection.commit()
        return result







