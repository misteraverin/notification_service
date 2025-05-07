import random

import pytest
from fastapi import status


async def create_phone_code(
    async_client_authenticated,
    pc: str = str(random.randint(100, 999)),
):
    phone_code = {'phone_code': pc}
    response = await async_client_authenticated.post(
        '/api/phone_codes/',
        json=phone_code
    )
    return phone_code, response


async def create_phone_codes(async_client_authenticated, qty: int = 1):
    return [
        await create_phone_code(async_client_authenticated, str(pc))
        for pc in random.sample(range(100, 999), qty)
    ]


@pytest.mark.asyncio
async def test_get_phone_codes(async_client):
    response = await async_client.get('/api/phone_codes/')
    phone_codes = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0
    assert all(['phone_code' in pc for pc in phone_codes])


@pytest.mark.asyncio
async def test_create_phone_code(async_client_authenticated):
    phone_code, response = await create_phone_code(async_client_authenticated)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['phone_code'] == phone_code['phone_code']


@pytest.mark.asyncio
async def test_get_phone_code(async_client_authenticated, async_client):
    phone_code, response_create = await create_phone_code(async_client_authenticated)

    response = await async_client.get(
        f"/api/phone_codes/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['phone_code'] == phone_code['phone_code']
    assert response.json()['id'] == response_create.json()['id']


@pytest.mark.asyncio
async def test_delete_phone_code(async_client_authenticated):
    phone_code, response_create = await create_phone_code(async_client_authenticated)

    response = await async_client_authenticated.delete(
        f"/api/phone_codes/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_phone_code(async_client_authenticated):
    phone_code, response_create = await create_phone_code(async_client_authenticated)
    new_phone_code = str(random.randint(100, 999))

    response = await async_client_authenticated.put(
        f"/api/phone_codes/{response_create.json()['id']}",
        json={'phone_code': new_phone_code},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['phone_code'] == new_phone_code
    assert response.json()['id'] == response_create.json()['id']


@pytest.mark.asyncio
async def test_get_phone_code_paginated(async_client, async_client_authenticated):
    await create_phone_codes(async_client_authenticated, qty=4)

    response_page_1 = await async_client.get('/api/phone_codes/?limit=2')
    assert len(response_page_1.json()) == 2

    response_page_2 = await async_client.get(
        '/api/phone_codes/?limit=2&offset=2'
    )
    assert len(response_page_2.json()) == 2

    response = await async_client.get('/api/phone_codes/')
    assert len(response.json()) == 4


@pytest.mark.asyncio
async def test_not_unique_phone_codes(async_client, async_client_authenticated):
    await async_client_authenticated.post('/api/phone_codes/', json={'phone_code': '980'})
    await async_client_authenticated.post('/api/phone_codes/', json={'phone_code': '980'})

    response = await async_client.get('/api/phone_codes/')
    assert len(response.json()) == 1
