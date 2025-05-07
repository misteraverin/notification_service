import random
import zoneinfo

import pytest
from fastapi import status


async def create_timezone(
    async_client_authenticated,
    tz: str = random.choice(list(zoneinfo.available_timezones())),
):
    timezone = {'timezone': tz}
    response = await async_client_authenticated.post(
        '/api/timezones/',
        json=timezone
    )
    return timezone, response


async def create_timezones(async_client_authenticated, qty: int = 1):
    return [
        await create_timezone(async_client_authenticated, pc)
        for pc in random.sample(list(zoneinfo.available_timezones()), qty)
    ]


@pytest.mark.asyncio
async def test_get_timezones(async_client):
    response = await async_client.get('/api/timezones/')
    timezones = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0
    assert all(['timezone' in tz for tz in timezones])


@pytest.mark.asyncio
async def test_create_timezone(async_client_authenticated):
    timezone, response = await create_timezone(async_client_authenticated)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['timezone'] == timezone['timezone']


@pytest.mark.asyncio
async def test_get_timezone(async_client_authenticated, async_client):
    timezone, response_create = await create_timezone(async_client_authenticated)

    response = await async_client.get(
        f"/api/timezones/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['timezone'] == timezone['timezone']
    assert response.json()['id'] == response_create.json()['id']


@pytest.mark.asyncio
async def test_delete_timezone(async_client_authenticated):
    timezone, response_create = await create_timezone(async_client_authenticated)

    response = await async_client_authenticated.delete(
        f"/api/timezones/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_timezone(async_client_authenticated):
    timezone, response_create = await create_timezone(async_client_authenticated)
    new_timezone = random.choice(list(zoneinfo.available_timezones()))

    response = await async_client_authenticated.put(
        f"/api/timezones/{response_create.json()['id']}",
        json={'timezone': new_timezone},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['timezone'] == new_timezone
    assert response.json()['id'] == response_create.json()['id']


@pytest.mark.asyncio
async def test_get_timezone_paginated(async_client, async_client_authenticated):
    await create_timezones(async_client_authenticated, qty=4)

    response_page_1 = await async_client.get('/api/timezones/?limit=2')
    assert len(response_page_1.json()) == 2

    response_page_2 = await async_client.get(
        '/api/timezones/?limit=2&offset=2'
    )
    assert len(response_page_2.json()) == 2

    response = await async_client.get('/api/timezones/')
    assert len(response.json()) == 4


@pytest.mark.asyncio
async def test_not_unique_timezones(async_client, async_client_authenticated):
    await async_client_authenticated.post('/api/timezones/', json={'timezone': 'Europe/Belgrade'})
    await async_client_authenticated.post('/api/timezones/', json={'timezone': 'Europe/Belgrade'})

    response = await async_client.get('/api/timezones/')
    assert len(response.json()) == 1
