import pytest
from fastapi import status


@pytest.mark.parametrize(
    'user_info, status_code',
    [
        ({'username': 'shark', 'password': 'qwerty'}, status.HTTP_200_OK),
        ({'username': 'fish', 'password': 'qwerty'}, status.HTTP_400_BAD_REQUEST),
        ({'username': 'shark', 'password': 'password'}, status.HTTP_400_BAD_REQUEST),
    ]
)
@pytest.mark.asyncio
async def test_login_user(create_user, async_client, user_info, status_code):
    await create_user()

    response = await async_client.post('/auth/token', data=user_info)

    assert response.status_code == status_code
