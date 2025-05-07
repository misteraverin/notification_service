from sqlmodel import SQLModel, Field, Relationship


class CustomerTag(SQLModel, table=True):
    __tablename__: str = 'customers_tags'
    customer_id: int | None = Field(
        default=None, foreign_key='customers.id', primary_key=True
    )
    tag_id: int | None = Field(
        default=None, foreign_key='tags.id', primary_key=True
    )


class MailoutTag(SQLModel, table=True):
    __tablename__: str = 'mailouts_tags'
    mailout_id: int | None = Field(
        default=None, foreign_key='mailouts.id', primary_key=True
    )
    tag_id: int | None = Field(
        default=None, foreign_key='tags.id', primary_key=True
    )


class MailoutPhoneCode(SQLModel, table=True):
    __tablename__: str = 'mailouts_phone_codes'
    mailout_id: int | None = Field(
        default=None, foreign_key='mailouts.id', primary_key=True
    )
    phone_code_id: int | None = Field(
        default=None, foreign_key='phone_codes.id', primary_key=True
    )
