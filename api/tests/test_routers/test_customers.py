import random

import pytest
from fastapi import status


async def create_customer(async_client_authenticated):
    phone_code_response = await async_client_authenticated.post(
        '/api/phone_codes/',
        json={'phone_code': '980'}
    )
    timezone_response = await async_client_authenticated.post(
        '/api/timezones/',
        json={'timezone': 'Europe/Belgrade'}
    )

    customer = {
        'country_code': random.randint(1, 9),
        'phone_code_id': phone_code_response.json()['id'],
        'phone': str(random.randint(1111111, 9999999)),
        'timezone_id': timezone_response.json()['id']
    }

    response = await async_client_authenticated.post(
        '/api/customers/',
        json=customer
    )
    return customer, response


async def create_customers(async_client_authenticated, qty: int = 1):
    return [
        await create_customer(async_client_authenticated)
        for _ in range(qty)
    ]


@pytest.mark.asyncio
async def test_get_customers(async_client):
    response = await async_client.get('/api/customers/')
    customers = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0
    assert all(['phone' in c for c in customers])


@pytest.mark.asyncio
async def test_create_customer(async_client_authenticated):
    customer, response = await create_customer(async_client_authenticated)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['country_code'] == customer['country_code']
    assert response.json()['phone_code_id'] == customer['phone_code_id']
    assert response.json()['phone'] == customer['phone']
    assert response.json()['timezone_id'] == customer['timezone_id']


@pytest.mark.asyncio
async def test_get_customer(async_client_authenticated, async_client):
    customer, response_create = await create_customer(async_client_authenticated)

    response = await async_client.get(
        f"/api/customers/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['country_code'] == customer['country_code']
    assert response.json()['phone_code_id'] == customer['phone_code_id']
    assert response.json()['phone'] == customer['phone']
    assert response.json()['timezone_id'] == customer['timezone_id']
    assert response.json()['id'] == response_create.json()['id']


@pytest.mark.asyncio
async def test_delete_customer(async_client_authenticated):
    customer, response_create = await create_customer(async_client_authenticated)

    response = await async_client_authenticated.delete(
        f"/api/customers/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_customer(async_client_authenticated):
    customer, response_create = await create_customer(async_client_authenticated)

    new_country_code = random.randint(1, 9)
    new_phone_code_id = 1
    new_phone = str(random.randint(1111111, 9999999))
    new_timezone_id = 1

    response = await async_client_authenticated.put(
        f"/api/customers/{response_create.json()['id']}",
        json={
            'country_code': new_country_code,
            'phone_code_id': new_phone_code_id,
            'phone': new_phone,
            'timezone_id': new_timezone_id,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['country_code'] == new_country_code
    assert response.json()['phone_code_id'] == new_phone_code_id
    assert response.json()['phone'] == new_phone
    assert response.json()['timezone_id'] == new_timezone_id
    assert response.json()['id'] == response_create.json()['id']


@pytest.mark.asyncio
async def test_get_customer_paginated(async_client, async_client_authenticated):
    await create_customers(async_client_authenticated, qty=4)

    response_page_1 = await async_client.get('/api/customers/?limit=2')
    assert len(response_page_1.json()) == 2

    response_page_2 = await async_client.get(
        '/api/customers/?limit=2&offset=2'
    )
    assert len(response_page_2.json()) == 2

    response = await async_client.get('/api/customers/')
    assert len(response.json()) == 4


@pytest.mark.asyncio
async def test_create_customer_tag(async_client_authenticated):
    customer, response_create = await create_customer(async_client_authenticated)

    response = await async_client_authenticated.post(
        f'/api/customers/{response_create.json()["id"]}/tags',
        json={'tag': 'Test'}
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_delete_customer_tag(async_client_authenticated):
    customer, response_create = await create_customer(async_client_authenticated)

    tag_created = await async_client_authenticated.post(
        f'/api/customers/{response_create.json()["id"]}/tags',
        json={'tag': 'Test'}
    )

    response = await async_client_authenticated.post(
        f'/api/customers/{response_create.json()["id"]}/tags/{tag_created.json()["id"]}'
    )

    assert response.status_code == status.HTTP_200_OK
