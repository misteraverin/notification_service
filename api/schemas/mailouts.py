from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .link_schemas import MailoutPhoneCode, MailoutTag
from .phone_codes import PhoneCodeRead
from .tags import TagRead

if TYPE_CHECKING:
    from .messages import Message
    from .phone_codes import PhoneCode, PhoneCodeRead
    from .tags import Tag, TagRead


class MailoutBase(SQLModel):
    text_message: str
    start_at: datetime
    finish_at: datetime
    local_time_start_hour: int | None = Field(
        default=None,
        description="Start hour for sending messages in client's local time (0-23)",
    )
    local_time_end_hour: int | None = Field(
        default=None,
        description="End hour for sending messages in client's local time (0-23)",
    )

    def requires_processing(self) -> bool:
        return self.start_at <= datetime.now() < self.finish_at

    class Config:
        schema_extra = {
            "example": {
                "text_message": "Test message",
                "start_at": datetime(2023, 6, 30, 10, 0, 0),
                "finish_at": datetime(2023, 6, 30, 11, 0, 0),
                "local_time_start_hour": 9,
                "local_time_end_hour": 17,
            }
        }


class Mailout(MailoutBase, table=True):
    __tablename__: str = "mailouts"

    id: int | None = Field(primary_key=True, default=None)
    tags: list["Tag"] = Relationship(back_populates="mailouts", link_model=MailoutTag)
    phone_codes: list["PhoneCode"] = Relationship(
        back_populates="mailouts", link_model=MailoutPhoneCode
    )
    messages: list["Message"] = Relationship(back_populates="mailout")


class MailoutCreate(MailoutBase):
    pass


class MailoutRead(MailoutBase):
    id: int
    phone_codes: list[PhoneCodeRead] = []
    tags: list[TagRead] = []
    local_time_start_hour: int | None = None
    local_time_end_hour: int | None = None


class MailoutUpdate(SQLModel):
    text_message: str | None
    start_at: datetime | None = None
    finish_at: datetime | None = None
    local_time_start_hour: int | None = None
    local_time_end_hour: int | None = None
