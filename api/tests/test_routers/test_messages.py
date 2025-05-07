import pytest
from fastapi import status

from schemas.base import StatusEnum
from tests.test_routers.test_customers import create_customer
from tests.test_routers.test_mailouts import create_mailout


async def create_message(async_client_authenticated):
    _, customer_response = await create_customer(async_client_authenticated)
    _, mailout_response = await create_mailout(async_client_authenticated)

    message = {
        'mailout_id': mailout_response.json()['id'],
        'customer_id': customer_response.json()['id']
    }

    response = await async_client_authenticated.post(
        '/api/messages/',
        json=message
    )
    return message, response


async def create_messages(async_client_authenticated, qty: int = 1):
    return [
        await create_message(async_client_authenticated)
        for _ in range(qty)
    ]


@pytest.mark.asyncio
async def test_get_messages(async_client):
    response = await async_client.get('/api/messages/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_create_message(async_client_authenticated):
    message, response = await create_message(async_client_authenticated)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['created_at'] is not None
    assert response.json()['status'] == StatusEnum.created
    assert response.json()['mailout_id'] == message['mailout_id']
    assert response.json()['customer_id'] == message['customer_id']


@pytest.mark.asyncio
async def test_get_message(async_client_authenticated, async_client):
    message, response_create = await create_message(async_client_authenticated)

    response = await async_client.get(
        f"/api/messages/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['created_at'] is not None
    assert response.json()['status'] == StatusEnum.created
    assert response.json()['mailout_id'] == message['mailout_id']
    assert response.json()['customer_id'] == message['customer_id']
    assert response.json()['id'] == response_create.json()['id']


@pytest.mark.asyncio
async def test_delete_message(async_client_authenticated):
    message, response_create = await create_message(async_client_authenticated)

    response = await async_client_authenticated.delete(
        f"/api/messages/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_message(async_client_authenticated):
    message, response_create = await create_message(async_client_authenticated)

    new_mailout_id = 1
    new_customer_id = 1

    response = await async_client_authenticated.put(
        f"/api/messages/{response_create.json()['id']}",
        json={
            'mailout_id': new_mailout_id,
            'customer_id': new_customer_id
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['mailout_id'] == new_mailout_id
    assert response.json()['customer_id'] == new_customer_id
    assert response.json()['id'] == response_create.json()['id']


@pytest.mark.asyncio
async def test_get_message_paginated(async_client, async_client_authenticated):
    await create_messages(async_client_authenticated, qty=4)

    response_page_1 = await async_client.get('/api/messages/?limit=2')
    assert len(response_page_1.json()) == 2

    response_page_2 = await async_client.get(
        '/api/messages/?limit=2&offset=2'
    )
    assert len(response_page_2.json()) == 2

    response = await async_client.get('/api/messages/')
    assert len(response.json()) == 4


@pytest.mark.asyncio
async def test_get_general_stats(async_client_authenticated, async_client):
    await create_message(async_client_authenticated)

    response = await async_client.get('/api/messages/stats')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['status'] == StatusEnum.created
    assert response.json()[0]['count'] == 1


@pytest.mark.asyncio
async def test_get_detailed_stats(async_client_authenticated, async_client):
    _, response_create = await create_message(async_client_authenticated)

    response = await async_client.get(
        f"/api/messages/stats/{response_create.json()['mailout_id']}"
        f"?status={response_create.json()['status']}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['status'] == StatusEnum.created
    assert response.json()[0]['count'] == 1
