from passlib.context import CryptContext
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field

pwd_context = CryptContext(schemes=['bcrypt'])


class UserBase(SQLModel):
    username: str = Field(index=True)


class User(UserBase, table=True):
    __tablename__: str = 'users'
    __table_args__ = (UniqueConstraint('username'),)

    id: int | None = Field(default=None, primary_key=True)
    password_hash: str = ''

    def set_password(self, password):
        """Setting the password actually sets password_hash."""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        """Verify given password by hashing and comparing to password_hash."""
        return pwd_context.verify(password, self.password_hash)


class UserRead(UserBase):
    id: int
    username: str
