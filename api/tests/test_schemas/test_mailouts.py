from datetime import datetime, time

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
            available_start_at=time(9, 0, 0),
            available_finish_at=time(18, 0, 0),
            text_message='Test message',
        )


def test_mailout_instance_finish_time_empty():
    with pytest.raises(expected_exception=ValidationError):
        MailoutCreate(
            start_at=datetime(2023, 7, 12),
            available_start_at=time(9, 0, 0),
            available_finish_at=time(18, 0, 0),
            text_message='Test message',
        )


def test_mailout_instance_available_start_empty():
    mailout = MailoutCreate(
        start_at=datetime(2023, 7, 12),
        finish_at=datetime(2023, 7, 13),
        available_finish_at=time(18, 0, 0),
        text_message='Test message',
    )
    assert mailout is not None


def test_mailout_instance_available_finish_empty():
    mailout = MailoutCreate(
        start_at=datetime(2023, 7, 12),
        finish_at=datetime(2023, 7, 13),
        available_start_at=time(9, 0, 0),
        text_message='Test message',
    )
    assert mailout is not None


def test_mailout_instance_wrong_format():
    with pytest.raises(expected_exception=ValidationError):
        MailoutCreate(
            start_at='2023/07/12',
            finish_at=2023,
            available_start_at='09:00',
            available_finish_at=18,
            text_message='Test message',
        )


def test_mailout_instance_message_empty():
    with pytest.raises(expected_exception=ValidationError):
        MailoutCreate(
            start_at=datetime(2023, 7, 11),
            finish_at=datetime(2023, 7, 12),
            available_start_at=time(9, 0, 0),
            available_finish_at=time(18, 0, 0),
        )
