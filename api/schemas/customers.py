from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from .tags import TagRead
from .link_schemas import CustomerTag

if TYPE_CHECKING:
    from .phone_codes import PhoneCode
    from .timezones import Timezone
    from .tags import Tag, TagRead
    from .messages import Message


class CustomerBase(SQLModel):
    country_code: int = Field(default=7)
    phone_code_id: int | None = Field(default=None, foreign_key='phone_codes.id')
    phone: str = Field(index=True)
    timezone_id: int | None = Field(default=1, foreign_key='timezones.id')

    class Config:
        schema_extra = {
            "example": {
                "country_code": 7,
                "phone_code_id": 1,
                "phone": "1234567",
                "timezone_id": 1
            }
        }


class Customer(CustomerBase, table=True):
    __tablename__: str = 'customers'

    id: int | None = Field(primary_key=True, default=None)

    phone_code: Optional['PhoneCode'] = Relationship(back_populates='customers')
    timezone: Optional['Timezone'] = Relationship(back_populates='customers')
    tags: list['Tag'] = Relationship(back_populates='customers', link_model=CustomerTag)
    messages: list['Message'] = Relationship(back_populates='customer')


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int
    tags: list[TagRead] = []


class CustomerUpdate(SQLModel):
    country_code: int | None = None
    phone_code_id: int | None = None
    phone: str | None = None
    timezone_id: int | None = None
