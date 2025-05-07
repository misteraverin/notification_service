from datetime import datetime

import pytest
from pydantic import ValidationError
from schemas.mailouts import MailoutCreate


def test_mailout_instance_empty():
    with pytest.raises(expected_exception=ValidationError):
        MailoutCreate()


def test_mailout_instance_start_time_empty():
    with pytest.raises(expected_exception=ValidationError):
        MailoutCreate(
            finish_at=datetime(2023, 7, 12),
            text_message="Test message",
        )


def test_mailout_instance_finish_time_empty():
    with pytest.raises(expected_exception=ValidationError):
        MailoutCreate(
            start_at=datetime(2023, 7, 12),
            text_message="Test message",
        )


def test_mailout_instance_wrong_format():
    with pytest.raises(expected_exception=ValidationError):
        MailoutCreate(
            start_at="2023/07/12",
            finish_at=2023,
            text_message="Test message",
        )


def test_mailout_instance_message_empty():
    with pytest.raises(expected_exception=ValidationError):
        MailoutCreate(
            start_at=datetime(2023, 7, 11),
            finish_at=datetime(2023, 7, 12),
            local_time_start_hour=9,
            local_time_end_hour=17,
        )


def test_mailout_instance_with_local_time_valid():
    try:
        mailout = MailoutCreate(
            text_message="Test message for local time",
            start_at=datetime(2023, 8, 1, 10, 0, 0),
            finish_at=datetime(2023, 8, 1, 12, 0, 0),
            local_time_start_hour=9,
            local_time_end_hour=17,
        )
        assert mailout.local_time_start_hour == 9
        assert mailout.local_time_end_hour == 17
    except ValidationError as e:
        pytest.fail(f"Validation failed for valid local time fields: {e}")


def test_mailout_instance_with_partial_local_time_valid():
    try:
        mailout = MailoutCreate(
            text_message="Test message for partial local time",
            start_at=datetime(2023, 8, 1, 10, 0, 0),
            finish_at=datetime(2023, 8, 1, 12, 0, 0),
            local_time_start_hour=9,
        )
        assert mailout.local_time_start_hour == 9
        assert mailout.local_time_end_hour is None
    except ValidationError as e:
        pytest.fail(f"Validation failed for partial local time fields: {e}")
