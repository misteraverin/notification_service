from typing import Generator

from asyncio import current_task
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from db.config import settings

engine = create_engine(
    url=settings.sync_database_url,
    echo=settings.db_echo_log,
)

async_engine = create_async_engine(
    url=settings.async_database_url,
    echo=settings.db_echo_log,
    future=True,
)

async_session = async_scoped_session(
    sessionmaker(
        async_engine,
        class_=AsyncSession,
    ),
    scopefunc=current_task,
)


def get_session() -> Generator:
    with Session(engine) as session:
        yield session


async def get_async_session() -> Generator:
    async with AsyncSession(async_engine) as session:
        yield session


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
        await session.commit()


def get_repository(repository):
    def _get_repository(session: AsyncSession = Depends(get_db)):
        return repository(session)
    return _get_repository
