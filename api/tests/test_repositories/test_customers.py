import random

import pytest

from db.errors import EntityDoesNotExist
from repositories.phone_codes import PhoneCodeRepository
from repositories.timezones import TimezoneRepository
from repositories.tags import TagRepository
from repositories.customers import CustomerRepository
from schemas.phone_codes import PhoneCodeCreate
from schemas.timezones import TimezoneCreate
from schemas.tags import TagCreate
from schemas.customers import Customer, CustomerCreate, CustomerUpdate


async def create_customer(db_session):
    phone_code_repo = PhoneCodeRepository(db_session)
    timezone_repo = TimezoneRepository(db_session)
    tag_repo = TagRepository(db_session)
    customer_repo = CustomerRepository(db_session)

    db_phone_code = await phone_code_repo.create(PhoneCodeCreate(phone_code='980'))
    db_timezone = await timezone_repo.create(TimezoneCreate(timezone='Europe/Belgrade'))

    customer = CustomerCreate(
        country_code=7,
        phone_code_id=db_phone_code.id,
        phone='9999999',
        timezone_id=db_timezone.id,
    )

    db_customer = await customer_repo.create(customer)

    db_tag = await tag_repo.create(
        model_id=db_customer.id,
        tag_create=TagCreate(tag='Test'),
        parent_model=Customer,
    )

    return customer_repo, customer, db_customer


@pytest.mark.asyncio
async def test_create_customer(db_session):
    _, customer, db_customer = await create_customer(db_session)

    assert db_customer.country_code == customer.country_code
    assert db_customer.phone_code_id == customer.phone_code_id
    assert db_customer.phone == customer.phone
    assert db_customer.timezone_id == customer.timezone_id


@pytest.mark.asyncio
async def test_get_customers(db_session):
    repository, customer, db_customer = await create_customer(db_session)

    db_customers = await repository.list()

    assert db_customers[0].country_code == customer.country_code
    assert db_customers[0].phone_code_id == customer.phone_code_id
    assert db_customers[0].phone == customer.phone
    assert db_customers[0].timezone_id == customer.timezone_id


@pytest.mark.asyncio
async def test_get_customer_by_id(db_session):
    repository, _, db_customer = await create_customer(db_session)

    found_customer = await repository.get(model_id=db_customer.id)

    assert db_customer == found_customer


@pytest.mark.asyncio
async def test_get_customer_by_id_not_found(db_session):
    repository = CustomerRepository(db_session)

    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=random.randint(2, 9))


@pytest.mark.asyncio
async def test_update_customer(db_session):
    new_country_code = random.randint(1, 9)
    new_phone_code_id = 1
    new_phone = str(random.randint(1111111, 9999999))
    new_timezone_id = 1

    repository, _, db_customer = await create_customer(db_session)

    update_customer = await repository.update(
        model_id=db_customer.id,
        model_update=CustomerUpdate(
            country_code=new_country_code,
            phone_code_id=new_phone_code_id,
            phone=new_phone,
            timezone_id=new_timezone_id,
        ),
    )

    assert update_customer.id == db_customer.id
    assert update_customer.country_code == new_country_code
    assert update_customer.phone_code_id == new_phone_code_id
    assert update_customer.phone == new_phone
    assert update_customer.timezone_id == new_timezone_id


@pytest.mark.asyncio
async def test_delete_customer(db_session):
    repository, _, db_customer = await create_customer(db_session)

    delete_customer = await repository.delete(model_id=db_customer.id, model=Customer)

    assert delete_customer is None
    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(model_id=db_customer.id)


@pytest.mark.asyncio
async def test_delete_customer_tag(db_session):
    repository, _, db_customer = await create_customer(db_session)

    repository.delete_customer_tag(model_id=1, tag_id=1)

    assert len(db_customer.tags) == 1
