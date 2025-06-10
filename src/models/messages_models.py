import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, Field

from settings import config


class SMSMessage(BaseModel):
    sender: str
    content: str
    received_date: datetime = Field(alias='date')
    partial: Optional[dict | str]
    service_id: str = config.app_modem_name

    @field_validator('partial', mode='before')
    def validate_partial(cls, v):
        if not isinstance(v, dict):
            return
        return json.dumps(v, ensure_ascii=False)


if __name__ == '__main__':
    package = {
        'sender': 'me',
        'content': 'hello!',
        'date': datetime.now(),
        'partial': {'key': 'value'}
    }
    sms = SMSMessage(**package)
    print(sms)