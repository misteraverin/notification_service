from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from .base import StatusEnum, TimeStampModel

if TYPE_CHECKING:
    from .mailouts import Mailout
    from .customers import Customer


class MessageBase(SQLModel):
    status: StatusEnum = Field(default=StatusEnum.created, index=True)
    mailout_id: int | None = Field(default=None, foreign_key='mailouts.id')
    customer_id: int | None = Field(default=None, foreign_key='customers.id')

    class Config:
        schema_extra = {
            "example": {
                "status": "Created",
                "mailout_id": 1,
                "customer_id": 1
            }
        }


class Message(MessageBase, TimeStampModel, table=True):
    __tablename__: str = 'messages'

    id: int | None = Field(primary_key=True, default=None)

    mailout: 'Mailout' = Relationship(back_populates='messages')
    customer: 'Customer' = Relationship(back_populates='messages')


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase, TimeStampModel):
    id: int


class MessageUpdate(SQLModel):
    status: Optional[str] = None
    mailout_id: int | None = None
    customer_id: int | None = None
