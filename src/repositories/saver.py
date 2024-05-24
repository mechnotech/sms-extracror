import csv
from typing import List

from models.messages_models import SMSMessage


class BaseSMSRepository:

    def __init__(self):
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
        fieldnames = ['sender', 'content', 'date', 'partial']
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
