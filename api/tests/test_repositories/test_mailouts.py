import random
from datetime import datetime

import pytest
from db.errors import EntityDoesNotExist, WrongDatetimeError
from repositories.mailouts import MailoutRepository
from repositories.phone_codes import PhoneCodeRepository
from repositories.tags import TagRepository
from schemas.mailouts import Mailout, MailoutCreate, MailoutUpdate
from schemas.phone_codes import PhoneCodeCreate
from schemas.tags import TagCreate


def get_right_mailout_create():
    return MailoutCreate(
        start_at=datetime(2023, 7, 12),
        finish_at=datetime(2023, 7, 13),
        text_message="Test message 1",
    )


def get_wrong_mailout_create():
    return MailoutCreate(
        start_at=datetime(2023, 7, 13),
        finish_at=datetime(2023, 7, 12),
        text_message="Test message 2",
    )


async def create_mailout(
    db_session,
    mailout: MailoutCreate = get_right_mailout_create(),
):
    mailout_repo = MailoutRepository(db_session)
    tag_repo = TagRepository(db_session)
    phone_code_repo = PhoneCodeRepository(db_session)

    db_mailout = await mailout_repo.create(mailout)

    db_tag = await tag_repo.create(
        model_id=db_mailout.id,
        tag_create=TagCreate(tag="Test"),
        parent_model=Mailout,
    )

    db_phone_code = await phone_code_repo.create(
        model_id=db_mailout.id,
        model_create=PhoneCodeCreate(phone_code=888),
        parent_model=Mailout,
    )

    return mailout_repo, mailout, db_mailout


@pytest.mark.asyncio
async def test_create_mailout(db_session):
    with pytest.raises(WrongDatetimeError):
        _, mailout, db_mailout = await create_mailout(
            db_session, get_wrong_mailout_create()
        )

    _, mailout, db_mailout = await create_mailout(db_session)

    assert db_mailout.start_at == mailout.start_at
    assert db_mailout.finish_at == mailout.finish_at
    assert db_mailout.text_message == mailout.text_message


@pytest.mark.asyncio
async def test_get_mailouts(db_session):
    repository, mailout, db_mailout = await create_mailout(db_session)

    db_mailouts = await repository.list()

    assert db_mailouts[0].start_at == mailout.start_at
    assert db_mailouts[0].finish_at == mailout.finish_at
    assert db_mailouts[0].text_message == mailout.text_message


@pytest.mark.asyncio
async def test_get_mailout_by_id(db_session):
    repository, _, db_mailout = await create_mailout(db_session)

    found_mailout = await repository.get(model_id=db_mailout.id)

    assert db_mailout == found_mailout


@pytest.mark.asyncio
async def test_get_mailout_by_id_not_found(db_session):
    repository = MailoutRepository(db_session)

    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=random.randint(2, 9))


@pytest.mark.asyncio
async def test_update_mailout(db_session):
    repository, _, db_mailout = await create_mailout(db_session)

    new_start_at = datetime(2024, 7, 12)
    new_finish_at = datetime(2024, 7, 13)
    new_text_message = "Text message 3"

    update_mailout = await repository.update(
        model_id=db_mailout.id,
        model_update=MailoutUpdate(
            start_at=new_start_at,
            finish_at=new_finish_at,
            text_message=new_text_message,
        ),
    )

    assert update_mailout.id == db_mailout.id
    assert update_mailout.start_at == new_start_at
    assert update_mailout.finish_at == new_finish_at
    assert update_mailout.text_message == new_text_message


@pytest.mark.asyncio
async def test_delete_mailout(db_session):
    repository, _, db_mailout = await create_mailout(db_session)

    delete_mailout = await repository.delete(model_id=db_mailout.id, model=Mailout)

    assert delete_mailout is None
    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=db_mailout.id)


@pytest.mark.asyncio
async def test_delete_mailout_tag(db_session):
    repository, _, db_mailout = await create_mailout(db_session)

    repository.delete_mailout_tag(model_id=1, tag_id=1)

    assert len(db_mailout.tags) == 1


@pytest.mark.asyncio
async def test_delete_mailout_phone_code(db_session):
    repository, _, db_mailout = await create_mailout(db_session)

    repository.delete_mailout_phone_code(model_id=1, phone_code_id=1)

    assert len(db_mailout.phone_codes) == 1
