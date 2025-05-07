from typing import Optional, TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .customers import Customer


class TimezoneBase(SQLModel):
    timezone: str

    class Config:
        schema_extra = {
            "example": {
                "timezone": "Europe/Belgrade"
            }
        }


class Timezone(TimezoneBase, table=True):
    __tablename__: str = 'timezones'
    __table_args__ = (UniqueConstraint('timezone'),)

    id: int | None = Field(default=None, primary_key=True)
    customers: list['Customer'] = Relationship(back_populates='timezone')


class TimezoneCreate(TimezoneBase):
    pass

    def __hash__(self):
        return hash(self.timezone)


class TimezoneRead(TimezoneBase):
    id: int


class TimezoneUpdate(SQLModel):
    timezone: Optional[str]
