from datetime import datetime

from sqlalchemy import Enum, text
from sqlmodel import Field, SQLModel


class StatusEnum(str, Enum):
    created = 'Created'
    updated = 'Updated'
    deleted = 'Deleted'
    pending = 'Pending'
    sent = 'Sent'
    failed = 'Failed'
    timed_out = 'Timed out'


class TimeStampModel(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={'server_default': text('current_timestamp(0)')},
    )
