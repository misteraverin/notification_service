import pytest
from pydantic import ValidationError

from schemas.phone_codes import PhoneCodeCreate


def test_phone_code_instance_empty():
    with pytest.raises(expected_exception=ValidationError):
        PhoneCodeCreate()
