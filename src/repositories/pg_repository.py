from typing import List

import psycopg2

from models.messages_models import SMSMessage, RecordedSMS
from settings import Settings


class PostgresRepository:
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

    def get_services(self):
        sql = 'select service_id from service.workflow'
        self.cur.execute(sql)
        result = self.cur.fetchall()
        if len(result) > 0:
            return [x[0] for x in result]
        raise Exception('service.workflow table is empty')

    def read_messages(self, top_id: int, name: str):
        sql = f"select * from service.sms_log where service_id = '{name}' and id > {top_id}"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        raw_records =  [
            RecordedSMS(
                id=r[0],
                sender=r[1],
                content=r[2],
                date=r[3],
                partial=r[4],
                service_id=r[5]
            )
            for r in result
        ]
        return raw_records

    def read_sql(self, sql: str):
        self.cur.execute(sql)
        result = self.cur.fetchone()
        return result

    def execute_sql(self, sql: str):
        self.cur.execute(sql)
        result = self.connection.commit()
        return result