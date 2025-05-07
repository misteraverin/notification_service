def test_user_password_hash(user_to_create):
    user = user_to_create

    assert isinstance(user.password_hash, str)
    assert user.verify_password('qwerty') is True
