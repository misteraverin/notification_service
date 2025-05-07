import random

import pytest

from db.errors import EntityDoesNotExist
from repositories.phone_codes import PhoneCodeRepository
from schemas.phone_codes import PhoneCode, PhoneCodeCreate, PhoneCodeUpdate


async def create_phone_code(db_session):
    repository = PhoneCodeRepository(db_session)
    phone_code = PhoneCodeCreate(phone_code='980')
    db_phone_code = await repository.create(phone_code)

    return repository, phone_code, db_phone_code


@pytest.mark.asyncio
async def test_create_phone_code(db_session):
    _, phone_code, db_phone_code = await create_phone_code(db_session)

    assert db_phone_code.phone_code == phone_code.phone_code


@pytest.mark.asyncio
async def test_get_phone_codes(db_session):
    repository, phone_code, db_phone_code = await create_phone_code(db_session)

    db_phone_codes = await repository.list()

    assert db_phone_codes[0].phone_code == phone_code.phone_code


@pytest.mark.asyncio
async def test_get_phone_code_by_id(db_session):
    repository, phone_code, db_phone_code = await create_phone_code(db_session)

    found_phone_code = await repository.get(model_id=db_phone_code.id)

    assert found_phone_code == db_phone_code


@pytest.mark.asyncio
async def test_get_phone_code_by_id_not_found(db_session):
    repository = PhoneCodeRepository(db_session)

    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=random.randint(2, 9))


@pytest.mark.asyncio
async def test_update_phone_code(db_session):
    new_phone_code = str(random.randint(100, 999))
    repository, _, db_phone_code = await create_phone_code(db_session)

    update_phone_code = await repository.update(
        model_id=db_phone_code.id,
        model_update=PhoneCodeUpdate(phone_code=new_phone_code),
    )

    assert update_phone_code.id == db_phone_code.id
    assert update_phone_code.phone_code == new_phone_code


@pytest.mark.asyncio
async def test_delete_phone_code(db_session):
    repository, _, db_phone_code = await create_phone_code(db_session)

    delete_phone_code = await repository.delete(model_id=db_phone_code.id, model=PhoneCode)

    assert delete_phone_code is None
    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=db_phone_code.id)
