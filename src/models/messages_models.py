from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class SMSMessage(BaseModel):
    sender: str
    content: str
    date: datetime
    partial: Optional[dict]

    @field_validator('partial', mode='before')
    def validate_partial(cls, v):
        if not isinstance(v, dict):
            return None
        return v
