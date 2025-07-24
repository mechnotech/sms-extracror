import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, Field

from settings import config


class SMSMessage(BaseModel):
    sender: str
    content: str
    received_date: datetime = Field(alias='date')
    partial: Optional[dict | str] = None
    service_id: str = config.app_modem_name

    @field_validator('partial', mode='before')
    def validate_partial(cls, v):
        if not isinstance(v, dict):
            return
        return json.dumps(v, ensure_ascii=False)

class RecordedSMS(SMSMessage):
    id: int
    part_reference: Optional[str] = None
    part_number: Optional[int] = None
    part_count: Optional[int] = None

class CompositeSMS(BaseModel):
    sender: str
    contents: list[RecordedSMS]
    full_text: Optional[str] = ''
    received_date: datetime = Field(alias='date')
    service_id: str = config.app_modem_name
    is_completed: bool = False
    parts_total: Optional[int] = None
    max_id: Optional[int] = None

    def check(self):
        if self.parts_total and len(self.contents) == self.parts_total:
            self.is_completed = True

        if not self.parts_total and len(self.contents) == 1:
            self.is_completed = True

        full_text = ' '.join([x.content for x in self.contents])
        self.full_text = full_text

        self.max_id = max(x.id for x in self.contents)

if __name__ == '__main__':
    package = {
        'id': 2,
        'sender': 'me',
        'content': 'hello!',
        'date': datetime.now(),
        'partial': {'key': 'value'}
    }
    sms = RecordedSMS(**package)
    sms2 = RecordedSMS(**package)
    ls = [sms, sms2]
    c_sms = CompositeSMS(
        sender='me',
        contents=ls,
        date=datetime.now(),
        parts_total=2

    )
    print(c_sms.full_text)
    c_sms.check()
    print(c_sms.full_text)
    c_sms_2 = CompositeSMS(
        sender='me',
        contents=[sms2],
        date=datetime.now(),
    )
    c_sms_2.check()
    print(c_sms_2.full_text)
