from typing import Optional, TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

from .link_schemas import CustomerTag, MailoutTag

if TYPE_CHECKING:
    from .customers import Customer
    from .mailouts import Mailout


class TagBase(SQLModel):
    tag: str


class Tag(TagBase, table=True):
    __tablename__: str = 'tags'
    __table_args__ = (UniqueConstraint('tag'),)

    id: int | None = Field(default=None, primary_key=True)
    customers: list['Customer'] = Relationship(back_populates='tags', link_model=CustomerTag, )
    mailouts: list['Mailout'] = Relationship(back_populates='tags', link_model=MailoutTag)


class TagCreate(TagBase):
    pass

    def __hash__(self):
        return hash(self.tag)


class TagRead(TagBase):
    id: int


class TagUpdate(SQLModel):
    tag: Optional[str] = None
