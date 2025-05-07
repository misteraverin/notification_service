from collections import namedtuple

import pytest

from db.errors import UserCredentialsError
from repositories.users import UserRepository

FormData = namedtuple('FormData', 'username password')


@pytest.mark.asyncio
async def test_login_user(create_user, db_session):
    await create_user()
    repository = UserRepository(db_session)

    user_logged_in = await repository.login(FormData('shark', 'qwerty'))

    assert user_logged_in['access_token'] is not None
    assert user_logged_in['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_wrong_login_user(create_user, db_session):
    await create_user()
    repository = UserRepository(db_session)

    with pytest.raises(expected_exception=UserCredentialsError):
        await repository.login(FormData('fish', 'qwerty'))
