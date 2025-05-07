import random

import pytest

from db.errors import EntityDoesNotExist
from repositories.tags import TagRepository
from schemas.tags import Tag, TagCreate, TagUpdate
from schemas.customers import Customer
from tests.test_repositories.test_customers import create_customer


async def create_tag(db_session):
    _, _, db_customer = await create_customer(db_session)

    repository = TagRepository(db_session)
    tag = TagCreate(tag='Test')
    db_tag = await repository.create(model_id=db_customer.id, tag_create=tag, parent_model=Customer)

    return repository, tag, db_tag


@pytest.mark.asyncio
async def test_create_tag(db_session):
    _, tag, db_tag = await create_tag(db_session)

    assert db_tag.tag == tag.tag


@pytest.mark.asyncio
async def test_get_tags(db_session):
    repository, tag, db_tag = await create_tag(db_session)

    db_tags = await repository.list(model=Tag)

    assert db_tags[0].tag == tag.tag


@pytest.mark.asyncio
async def test_get_tag_by_id(db_session):
    repository, tag, db_tag = await create_tag(db_session)

    found_tag = await repository.get(model_id=db_tag.id)

    assert found_tag == db_tag


@pytest.mark.asyncio
async def test_get_tag_by_id_not_found(db_session):
    repository = TagRepository(db_session)

    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=random.randint(2, 9))


@pytest.mark.asyncio
async def test_update_tag(db_session):
    new_tag = 'Tag'
    repository, _, db_tag = await create_tag(db_session)

    update_tag = await repository.update(
        model_id=db_tag.id,
        model_update=TagUpdate(tag=new_tag),
    )

    assert update_tag.id == db_tag.id
    assert update_tag.tag == new_tag


@pytest.mark.asyncio
async def test_delete_tag(db_session):
    repository, _, db_tag = await create_tag(db_session)

    delete_tag = await repository.delete(model_id=db_tag.id, model=Tag)

    assert delete_tag is None
    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=db_tag.id)
