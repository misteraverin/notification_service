import pytest
from fastapi import status

from tests.test_routers.test_customers import create_customer


async def create_tag(async_client_authenticated):
    _, customer_response = await create_customer(async_client_authenticated)

    response_create = await async_client_authenticated.post(
        f'/api/customers/{customer_response.json()["id"]}/tags',
        json={'tag': 'Test'}
    )

    return response_create


@pytest.mark.asyncio
async def test_delete_tag(async_client_authenticated):
    response_create = await create_tag(async_client_authenticated)

    response = await async_client_authenticated.delete(
        f"/api/tags/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_tag(async_client_authenticated):
    response_create = await create_tag(async_client_authenticated)
    new_tag = 'Tag'

    response = await async_client_authenticated.put(
        f"/api/tags/{response_create.json()['id']}",
        json={'tag': new_tag},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['tag'] == new_tag
    assert response.json()['id'] == response_create.json()['id']


@pytest.mark.asyncio
async def test_not_unique_tags(async_client, async_client_authenticated):
    _, customer_response = await create_customer(async_client_authenticated)

    await async_client_authenticated.post(
        f'/api/customers/{customer_response.json()["id"]}/tags',
        json={'tag': 'Test'}
    )
    await async_client_authenticated.post(
        f'/api/customers/{customer_response.json()["id"]}/tags',
        json={'tag': 'Test'}
    )

    response = await async_client.get(f'/api/customers/{customer_response.json()["id"]}')
    assert len(response.json()['tags']) == 1
