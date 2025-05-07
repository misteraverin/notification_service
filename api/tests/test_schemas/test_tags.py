import pytest
from pydantic import ValidationError

from schemas.tags import TagCreate


def test_tag_instance_empty():
    with pytest.raises(expected_exception=ValidationError):
        TagCreate()
