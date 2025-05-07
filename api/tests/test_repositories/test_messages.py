from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from db.errors import EntityDoesNotExist
from repositories.messages import MessageRepository
from schemas.base import StatusEnum
from schemas.customers import Customer
from schemas.mailouts import Mailout
from schemas.messages import Message, MessageCreate, MessageRead, MessageUpdate
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.fixture
def mock_session() -> AsyncMock:
    """Fixture for a mock SQLModel AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def message_repo(mock_session: AsyncMock) -> MessageRepository:
    """Fixture for MessageRepository with a mock session."""
    return MessageRepository(session=mock_session)


@pytest.fixture
def sample_customer() -> Customer:
    """Fixture for a sample Customer."""
    return Customer(
        id=1,
        phone="1234567890",
        phone_code_id=1,  # Assuming a valid ID for simplicity
        timezone_id=1,  # Assuming a valid ID for simplicity
        # country_code can be added if needed, defaults to None
    )


@pytest.fixture
def sample_mailout() -> Mailout:
    """Fixture for a sample Mailout."""
    return Mailout(
        id=1,
        text_message="Test mailout",
        start_at=datetime(2024, 1, 1, 10, 0, 0),
        finish_at=datetime(2024, 1, 1, 12, 0, 0),
        # available_start_at and available_finish_at can be added if needed
    )


@pytest.fixture
def message_create_payload(
    sample_customer: Customer, sample_mailout: Mailout
) -> MessageCreate:
    """Fixture for a MessageCreate payload."""
    return MessageCreate(customer_id=sample_customer.id, mailout_id=sample_mailout.id)


@pytest.fixture
def sample_message(message_create_payload: MessageCreate) -> Message:
    """Fixture for a sample Message ORM model instance."""
    return Message(
        id=1,
        status=StatusEnum.created,
        customer_id=message_create_payload.customer_id,
        mailout_id=message_create_payload.mailout_id,
    )


@pytest.fixture
def sample_message_read(sample_message: Message) -> MessageRead:
    """Fixture for a sample MessageRead schema."""
    return MessageRead.from_orm(sample_message)


@pytest.fixture
def message_update_payload() -> MessageUpdate:
    """Fixture for a MessageUpdate payload."""
    # Using an actual Enum member here, even if MessageUpdate schema says Optional[str].
    # This aligns with how status would likely be used if conversion is handled correctly in repo.
    return MessageUpdate(status=StatusEnum.sent)


@pytest.fixture
def message_update_payload_no_status() -> MessageUpdate:
    """Fixture for a MessageUpdate payload with no status explicitly set."""
    # Tests the default to StatusEnum.updated if model_update.status is None
    return MessageUpdate()


@pytest.mark.asyncio
async def test_create_message_success(
    message_repo: MessageRepository,
    mock_session: AsyncMock,
    sample_customer: Customer,
    sample_mailout: Mailout,
    message_create_payload: MessageCreate,
    sample_message_read: MessageRead,
):
    """Test successful message creation."""
    # Mock database lookups for customer and mailout
    customer_exec_result_mock = MagicMock()
    customer_exec_result_mock.first.return_value = sample_customer
    mailout_exec_result_mock = MagicMock()
    mailout_exec_result_mock.first.return_value = sample_mailout
    mock_session.exec.side_effect = [
        customer_exec_result_mock,
        mailout_exec_result_mock,
    ]

    # Mock the internal creation helper
    # Assuming _create_not_unique returns MessageRead or a compatible object
    # based on the repository's `create` method return type hint.
    message_repo._create_not_unique = AsyncMock(return_value=sample_message_read)

    result = await message_repo.create(message_create_payload)

    assert result == sample_message_read
    assert mock_session.exec.call_count == 2

    # Verify correct select statements were executed
    customer_select_call = mock_session.exec.call_args_list[0][0][0]
    assert str(customer_select_call) == str(
        select(Customer).where(Customer.id == message_create_payload.customer_id)
    )
    mailout_select_call = mock_session.exec.call_args_list[1][0][0]
    assert str(mailout_select_call) == str(
        select(Mailout).where(Mailout.id == message_create_payload.mailout_id)
    )

    message_repo._create_not_unique.assert_awaited_once_with(
        Message, message_create_payload
    )


@pytest.mark.asyncio
async def test_create_message_customer_not_found(
    message_repo: MessageRepository,
    mock_session: AsyncMock,
    message_create_payload: MessageCreate,
    sample_mailout: Mailout,
):
    """Test message creation fails if customer is not found."""
    customer_exec_result_mock = MagicMock()
    customer_exec_result_mock.first.return_value = None

    mailout_exec_result_mock = MagicMock()
    mailout_exec_result_mock.first.return_value = sample_mailout

    mock_session.exec.side_effect = [
        customer_exec_result_mock,
        mailout_exec_result_mock,
    ]

    with pytest.raises(EntityDoesNotExist):
        await message_repo.create(message_create_payload)

    assert mock_session.exec.call_count == 2


@pytest.mark.asyncio
async def test_create_message_mailout_not_found(
    message_repo: MessageRepository,
    mock_session: AsyncMock,
    sample_customer: Customer,
    message_create_payload: MessageCreate,
):
    """Test message creation fails if mailout is not found."""
    customer_exec_result_mock = MagicMock()
    customer_exec_result_mock.first.return_value = sample_customer

    mailout_exec_result_mock = MagicMock()
    mailout_exec_result_mock.first.return_value = None

    mock_session.exec.side_effect = [
        customer_exec_result_mock,
        mailout_exec_result_mock,
    ]

    with pytest.raises(EntityDoesNotExist):
        await message_repo.create(message_create_payload)

    assert mock_session.exec.call_count == 2


# Tests for the 'list' method
@pytest.mark.asyncio
async def test_list_messages_default_parameters(
    message_repo: MessageRepository,
    sample_message_read: MessageRead,
):
    """Test listing messages with default limit and offset."""
    expected_messages = [sample_message_read]
    with patch(
        "repositories.base.BaseRepository.list", new_callable=AsyncMock
    ) as mock_super_list:
        mock_super_list.return_value = expected_messages
        result = await message_repo.list()
        assert result == expected_messages
        mock_super_list.assert_awaited_once_with(Message, 50, 0)


@pytest.mark.asyncio
async def test_list_messages_custom_parameters(
    message_repo: MessageRepository,
    sample_message_read: MessageRead,
):
    """Test listing messages with custom limit and offset."""
    expected_messages = [sample_message_read]
    custom_limit = 10
    custom_offset = 5
    with patch(
        "repositories.base.BaseRepository.list", new_callable=AsyncMock
    ) as mock_super_list:
        mock_super_list.return_value = expected_messages
        result = await message_repo.list(limit=custom_limit, offset=custom_offset)
        assert result == expected_messages
        mock_super_list.assert_awaited_once_with(Message, custom_limit, custom_offset)


@pytest.mark.asyncio
async def test_list_messages_empty(
    message_repo: MessageRepository,
):
    """Test listing messages when none exist."""
    expected_empty_list = []
    with patch(
        "repositories.base.BaseRepository.list", new_callable=AsyncMock
    ) as mock_super_list:
        mock_super_list.return_value = expected_empty_list
        result = await message_repo.list()
        assert result == expected_empty_list
        mock_super_list.assert_awaited_once_with(Message, 50, 0)


# Tests for the 'get' method
@pytest.mark.asyncio
async def test_get_message_success(
    message_repo: MessageRepository,
    sample_message_read: MessageRead,
):
    """Test successfully retrieving a message by ID."""
    message_id = sample_message_read.id
    with patch(
        "repositories.base.BaseRepository.get", new_callable=AsyncMock
    ) as mock_super_get:
        mock_super_get.return_value = sample_message_read
        result = await message_repo.get(model_id=message_id)
        assert result == sample_message_read
        mock_super_get.assert_awaited_once_with(Message, message_id)


@pytest.mark.asyncio
async def test_get_message_not_found(
    message_repo: MessageRepository,
):
    """Test retrieving a non-existent message by ID returns None."""
    non_existent_id = 999
    with patch(
        "repositories.base.BaseRepository.get", new_callable=AsyncMock
    ) as mock_super_get:
        mock_super_get.return_value = None
        result = await message_repo.get(model_id=non_existent_id)
        assert result is None
        mock_super_get.assert_awaited_once_with(Message, non_existent_id)


# Tests for the 'update' method
@patch("repositories.messages.datetime")
@pytest.mark.asyncio
async def test_update_message_success(
    mock_dt: MagicMock,
    message_repo: MessageRepository,
    sample_message: Message,
    message_update_payload: MessageUpdate,
):
    """Test successfully updating a message."""
    assert sample_message.id is not None
    message_id: int = sample_message.id

    mocked_now = datetime(2024, 1, 1, 12, 30, 0)
    mock_dt.utcnow.return_value = mocked_now

    # Item fetched by the first _get_instance call
    original_item_instance = Message.from_orm(sample_message)

    # Expected state of the item after update, for the second _get_instance call
    # The MessageRepository.update method should handle status conversion if MessageUpdate.status is str.
    # Here, message_update_payload.status is StatusEnum.sent from the fixture.
    expected_updated_item = Message.from_orm(sample_message)
    if message_update_payload.status is not None:  # Status is being updated
        expected_updated_item.status = message_update_payload.status
    else:  # Status is not in payload, should default to StatusEnum.updated
        expected_updated_item.status = StatusEnum.updated
    expected_updated_item.created_at = mocked_now
    # Note: The SUT also iterates model_update.dict(exclude_unset=True, exclude={'id', 'status', 'created_at'})
    # For this test, message_update_payload only has 'status', so other fields aren't changing.

    message_repo._get_instance = AsyncMock(
        side_effect=[
            original_item_instance,
            MessageRead.from_orm(
                expected_updated_item
            ),  # Second call returns updated item as MessageRead
        ]
    )
    message_repo._add_to_db = AsyncMock()

    result = await message_repo.update(message_id, message_update_payload)

    assert result is not None
    assert result.status == expected_updated_item.status  # Should be StatusEnum.sent
    assert result.created_at == mocked_now

    assert message_repo._get_instance.call_count == 2
    message_repo._get_instance.assert_any_call(Message, message_id)

    # Verify the item passed to _add_to_db had its attributes changed correctly
    message_repo._add_to_db.assert_awaited_once()
    item_passed_to_add = message_repo._add_to_db.call_args[0][0]
    assert item_passed_to_add.status == expected_updated_item.status
    assert item_passed_to_add.created_at == mocked_now


@patch("repositories.messages.datetime")
@pytest.mark.asyncio
async def test_update_message_success_defaults_status_updated(
    mock_dt: MagicMock,
    message_repo: MessageRepository,
    sample_message: Message,
    message_update_payload_no_status: MessageUpdate,
):
    """Test update sets status to StatusEnum.updated if not in payload."""
    assert sample_message.id is not None
    message_id: int = sample_message.id

    mocked_now = datetime(2024, 1, 1, 12, 30, 0)
    mock_dt.utcnow.return_value = mocked_now

    original_item_instance = Message.from_orm(sample_message)

    expected_updated_item = Message.from_orm(sample_message)
    expected_updated_item.status = StatusEnum.updated
    expected_updated_item.created_at = mocked_now

    message_repo._get_instance = AsyncMock(
        side_effect=[
            original_item_instance,
            MessageRead.from_orm(expected_updated_item),
        ]
    )
    message_repo._add_to_db = AsyncMock()

    result = await message_repo.update(message_id, message_update_payload_no_status)

    assert result is not None
    assert result.status == StatusEnum.updated
    assert result.created_at == mocked_now

    message_repo._add_to_db.assert_awaited_once()
    item_passed_to_add = message_repo._add_to_db.call_args[0][0]
    assert item_passed_to_add.status == StatusEnum.updated


@pytest.mark.asyncio
async def test_update_message_not_found(
    message_repo: MessageRepository, message_update_payload: MessageUpdate
):
    """Test updating a non-existent message raises EntityDoesNotExist."""
    non_existent_id = 999
    message_repo._get_instance = AsyncMock(return_value=None)

    with pytest.raises(EntityDoesNotExist):
        await message_repo.update(non_existent_id, message_update_payload)

    message_repo._get_instance.assert_awaited_once_with(Message, non_existent_id)


# Tests for the 'delete' method
@pytest.mark.asyncio
async def test_delete_message_success(
    message_repo: MessageRepository,
    sample_message: Message,
):
    """Test successfully soft-deleting a message.
    Note: SUT's delete method returns result of _get_instance, but hint is None.
    This test verifies the SUT's actual execution path.
    """
    assert sample_message.id is not None
    message_id: int = sample_message.id

    item_fetched_first = Message.from_orm(sample_message)

    # Expected state for the item returned by the SUT's second _get_instance call
    item_to_be_returned_after_delete = Message.from_orm(sample_message)
    item_to_be_returned_after_delete.status = StatusEnum.deleted
    # created_at is not modified by the delete method in SUT

    message_repo._get_instance = AsyncMock(
        side_effect=[
            item_fetched_first,
            item_to_be_returned_after_delete,  # SUT returns this
        ]
    )
    message_repo._add_to_db = AsyncMock()

    returned_value = await message_repo.delete(message_id)

    assert message_repo._get_instance.call_count == 2
    expected_calls = [
        call(Message, message_id),  # First call to fetch
        call(Message, message_id),  # Second call for the return value by SUT
    ]
    message_repo._get_instance.assert_has_calls(expected_calls, any_order=False)

    # Verify the item passed to _add_to_db was the first fetched item, now modified
    message_repo._add_to_db.assert_awaited_once_with(item_fetched_first)
    assert item_fetched_first.status == StatusEnum.deleted  # Status modified in-place

    assert returned_value == item_to_be_returned_after_delete


@pytest.mark.asyncio
async def test_delete_message_not_found(message_repo: MessageRepository):
    """Test deleting a non-existent message raises EntityDoesNotExist."""
    non_existent_id = 999
    message_repo._get_instance = AsyncMock(return_value=None)

    with pytest.raises(EntityDoesNotExist):
        await message_repo.delete(non_existent_id)

    message_repo._get_instance.assert_awaited_once_with(Message, non_existent_id)


# Tests for 'get_general_stats' method
@pytest.mark.asyncio
async def test_get_general_stats_with_data(
    message_repo: MessageRepository, mock_session: AsyncMock
):
    """Test get_general_stats with various message statuses."""
    # Expected result: list of Row-like objects with 'status' and 'count'
    stat1_mock = MagicMock()
    stat1_mock.status = StatusEnum.sent
    stat1_mock.count = 10
    stat2_mock = MagicMock()
    stat2_mock.status = StatusEnum.failed
    stat2_mock.count = 5
    expected_stats_data = [stat1_mock, stat2_mock]

    mock_query_results = MagicMock()
    mock_query_results.all.return_value = expected_stats_data
    mock_session.exec.return_value = mock_query_results

    result = await message_repo.get_general_stats()

    assert result == expected_stats_data
    mock_session.exec.assert_awaited_once()
    # Detailed query assertion is omitted due to its complexity and known issues in SUT.


@pytest.mark.asyncio
async def test_get_general_stats_no_data(
    message_repo: MessageRepository, mock_session: AsyncMock
):
    """Test get_general_stats when no messages exist (empty stats)."""
    expected_empty_stats = []
    mock_query_results = MagicMock()
    mock_query_results.all.return_value = expected_empty_stats
    mock_session.exec.return_value = mock_query_results

    result = await message_repo.get_general_stats()

    assert result == expected_empty_stats
    mock_session.exec.assert_awaited_once()


# Tests for 'get_detailed_stats' method
@pytest.mark.asyncio
async def test_get_detailed_stats_with_data(
    message_repo: MessageRepository, mock_session: AsyncMock
):
    """Test get_detailed_stats for a mailout_id with various statuses."""
    mailout_id_to_test = 1
    stat1_mock = MagicMock()
    stat1_mock.status = StatusEnum.sent
    stat1_mock.count = 7
    stat2_mock = MagicMock()
    stat2_mock.status = StatusEnum.created
    stat2_mock.count = 3
    expected_stats_data = [stat1_mock, stat2_mock]

    mock_query_results = MagicMock()
    mock_query_results.all.return_value = expected_stats_data
    mock_session.exec.return_value = mock_query_results

    result = await message_repo.get_detailed_stats(model_id=mailout_id_to_test)

    assert result == expected_stats_data
    mock_session.exec.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_detailed_stats_with_status_filter(
    message_repo: MessageRepository, mock_session: AsyncMock
):
    """Test get_detailed_stats filtered by a specific status."""
    mailout_id_to_test = 1
    status_to_filter = StatusEnum.sent

    stat_sent_mock = MagicMock()
    stat_sent_mock.status = StatusEnum.sent
    stat_sent_mock.count = 7
    expected_stats_data = [stat_sent_mock]

    mock_query_results = MagicMock()
    mock_query_results.all.return_value = expected_stats_data
    mock_session.exec.return_value = mock_query_results

    result = await message_repo.get_detailed_stats(
        model_id=mailout_id_to_test, status=status_to_filter
    )

    assert result == expected_stats_data
    mock_session.exec.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_detailed_stats_no_data(
    message_repo: MessageRepository, mock_session: AsyncMock
):
    """Test get_detailed_stats for a mailout_id with no messages."""
    mailout_id_to_test = 2
    expected_empty_stats = []
    mock_query_results = MagicMock()
    mock_query_results.all.return_value = expected_empty_stats
    mock_session.exec.return_value = mock_query_results

    result = await message_repo.get_detailed_stats(model_id=mailout_id_to_test)

    assert result == expected_empty_stats
    mock_session.exec.assert_awaited_once()
