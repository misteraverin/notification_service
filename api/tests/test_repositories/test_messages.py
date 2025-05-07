import random

import pytest

from db.errors import EntityDoesNotExist
from repositories.messages import MessageRepository
from schemas.base import StatusEnum
from schemas.messages import Message, MessageCreate, MessageUpdate
from tests.test_repositories.test_customers import create_customer
from tests.test_repositories.test_mailouts import create_mailout


async def create_message(db_session):
    _, _, db_mailout = await create_mailout(db_session)
    _, _, db_customer = await create_customer(db_session)

    repository = MessageRepository(db_session)

    message = MessageCreate(
        mailout_id=db_mailout.id,
        customer_id=db_customer.id
    )

    db_message = await repository.create(message)

    return repository, message, db_message


@pytest.mark.asyncio
async def test_create_message(db_session):
    _, message, db_message = await create_message(db_session)

    assert db_message.created_at is not None
    assert db_message.status == StatusEnum.created
    assert db_message.mailout_id == message.mailout_id
    assert db_message.customer_id == message.customer_id


@pytest.mark.asyncio
async def test_get_messages(db_session):
    repository, message, db_message = await create_message(db_session)

    db_messages = await repository.list()

    assert db_messages[0].created_at is not None
    assert db_messages[0].status == StatusEnum.created
    assert db_messages[0].mailout_id == message.mailout_id
    assert db_messages[0].customer_id == message.customer_id


@pytest.mark.asyncio
async def test_get_message_by_id(db_session):
    repository, _, db_message = await create_message(db_session)

    found_message = await repository.get(model_id=db_message.id)

    assert db_message == found_message


@pytest.mark.asyncio
async def test_get_message_by_id_not_found(db_session):
    repository = MessageRepository(db_session)

    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=random.randint(2, 9))


@pytest.mark.asyncio
async def test_update_message(db_session):
    new_mailout_id = 1
    new_customer_id = 1

    repository, _, db_message = await create_message(db_session)

    update_message = await repository.update(
        model_id=db_message.id,
        model_update=MessageUpdate(
            mailout_id=new_mailout_id,
            customer_id=new_customer_id
        ),
    )

    assert update_message.id == db_message.id
    assert update_message.status == StatusEnum.updated
    assert update_message.mailout_id == new_mailout_id
    assert update_message.customer_id == new_customer_id


@pytest.mark.asyncio
async def test_delete_message(db_session):
    repository, _, db_message = await create_message(db_session)

    delete_message = await repository.delete(model_id=db_message.id)

    assert delete_message.status == StatusEnum.deleted


@pytest.mark.asyncio
async def test_get_general_stats(db_session):
    repository, _, db_message = await create_message(db_session)

    stats = await repository.get_general_stats()

    assert stats[0].status == StatusEnum.created
    assert stats[0].count == 1


@pytest.mark.asyncio
async def test_get_detailed_stats(db_session):
    repository, _, db_message = await create_message(db_session)

    stats = await repository.get_detailed_stats(
        model_id=db_message.mailout_id,
        status=db_message.status,
    )

    assert stats[0].status == StatusEnum.created
    assert stats[0].count == 1
