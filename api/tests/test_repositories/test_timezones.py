import random

import pytest

from db.errors import EntityDoesNotExist, TimezoneError
from repositories.timezones import TimezoneRepository
from schemas.timezones import Timezone, TimezoneCreate, TimezoneUpdate


async def create_timezone(db_session):
    repository = TimezoneRepository(db_session)
    timezone = TimezoneCreate(timezone='Europe/Belgrade')
    db_timezone = await repository.create(timezone)

    return repository, timezone, db_timezone


@pytest.mark.asyncio
async def test_create_timezone(db_session):
    _, timezone, db_timezone = await create_timezone(db_session)

    assert db_timezone.timezone == timezone.timezone


@pytest.mark.asyncio
async def test_create_wrong_timezone(db_session):
    repository = TimezoneRepository(db_session)

    with pytest.raises(expected_exception=TimezoneError):
        await repository.create(TimezoneCreate(timezone='Test'))


@pytest.mark.asyncio
async def test_get_timezone(db_session):
    repository, timezone, db_timezone = await create_timezone(db_session)

    db_timezones = await repository.list()

    assert db_timezones[0].timezone == timezone.timezone


@pytest.mark.asyncio
async def test_get_timezone_by_id(db_session):
    repository, timezone, db_timezone = await create_timezone(db_session)

    found_timezone = await repository.get(model_id=db_timezone.id)

    assert db_timezone == found_timezone


@pytest.mark.asyncio
async def test_get_timezone_by_id_not_found(db_session):
    repository = TimezoneRepository(db_session)

    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=random.randint(2, 9))


@pytest.mark.asyncio
async def test_update_timezone(db_session):
    new_timezone = 'Europe/Belgrade'
    repository, timezone, db_timezone = await create_timezone(db_session)

    update_timezone = await repository.update(
        model_id=db_timezone.id,
        model_update=TimezoneUpdate(timezone=new_timezone),
    )

    assert update_timezone.id == db_timezone.id
    assert update_timezone.timezone == new_timezone


@pytest.mark.asyncio
async def test_delete_timezone(db_session):
    repository, timezone, db_timezone = await create_timezone(db_session)

    delete_timezone = await repository.delete(model_id=db_timezone.id, model=Timezone)

    assert delete_timezone is None
    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=db_timezone.id)
