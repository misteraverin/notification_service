from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

from .link_schemas import MailoutPhoneCode

if TYPE_CHECKING:
    from .customers import Customer
    from .mailouts import Mailout


class PhoneCodeBase(SQLModel):
    phone_code: str

    class Config:
        schema_extra = {
            "example": {
                "phone_code": '950'
            }
        }


class PhoneCode(PhoneCodeBase, table=True):
    __tablename__: str = 'phone_codes'
    __table_args__ = (UniqueConstraint('phone_code'),)

    id: int | None = Field(default=None, primary_key=True)
    customers: list['Customer'] = Relationship(back_populates='phone_code')
    mailouts: list['Mailout'] = Relationship(
        back_populates='phone_codes', link_model=MailoutPhoneCode
    )


class PhoneCodeCreate(PhoneCodeBase):
    pass

    def __hash__(self):
        return hash(self.phone_code)


class PhoneCodeRead(PhoneCodeBase):
    id: int


class PhoneCodeUpdate(SQLModel):
    phone_code: str | None = None
