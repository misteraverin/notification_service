import pytest
from pydantic import ValidationError

from schemas.timezones import TimezoneCreate


def test_timezone_instance_empty():
    with pytest.raises(expected_exception=ValidationError):
        TimezoneCreate()
