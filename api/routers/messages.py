from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from db.errors import EntityDoesNotExist
from db.sessions import get_repository
from repositories.messages import MessageRepository
from routers.users import get_current_user
from schemas.messages import Message, MessageCreate, MessageRead, MessageUpdate
from schemas.users import User

router = APIRouter(prefix='/messages')


@router.post(
    '/',
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
    name='create_message',
)
async def create_message(
    message_create: MessageCreate = Body(...),
    repository: MessageRepository = Depends(get_repository(MessageRepository)),
    user: User = Depends(get_current_user),
) -> MessageRead:
    try:
        return await repository.create(model_create=message_create)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Customer or mailout not found'
        )


@router.get(
    '/',
    response_model=list[Optional[MessageRead]],
    status_code=status.HTTP_200_OK,
    name='get_messages',
)
async def get_messages(
    limit: int = Query(default=50, lte=100),
    offset: int = Query(default=0),
    repository: MessageRepository = Depends(get_repository(MessageRepository))
) -> list[Optional[MessageRead]]:
    return await repository.list(limit=limit, offset=offset)


@router.get(
    '/stats',
    status_code=status.HTTP_200_OK,
    name='get_general_stats',
)
async def get_general_stats(
    repository: MessageRepository = Depends(get_repository(MessageRepository))
) -> list:
    return await repository.get_general_stats()


@router.get(
    '/stats/{mailout_id}',
    status_code=status.HTTP_200_OK,
    name='get_detailed_stats',
)
async def get_detailed_stats(
    mailout_id: int,
    status: str | None = Query(default=None),
    repository: MessageRepository = Depends(get_repository(MessageRepository))
) -> list:
    return await repository.get_detailed_stats(model_id=mailout_id, status=status)


@router.get(
    '/{message_id}',
    response_model=MessageRead,
    status_code=status.HTTP_200_OK,
    name='get_message',
)
async def get_message(
    message_id: int,
    repository: MessageRepository = Depends(get_repository(MessageRepository)),
) -> MessageRead:
    try:
        result = await repository.get(model_id=message_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Message with ID={message_id} not found'
        )
    return result


@router.put(
    '/{message_id}',
    response_model=MessageRead,
    status_code=status.HTTP_200_OK,
    name='update_message',
)
async def update_message(
    message_id: int,
    message_update: MessageUpdate = Body(...),
    repository: MessageRepository = Depends(get_repository(MessageRepository)),
    user: User = Depends(get_current_user),
) -> MessageRead:
    try:
        await repository.get(model_id=message_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Message with ID={message_id} not found'
        )
    return await repository.update(model_id=message_id, model_update=message_update)


@router.delete(
    '/{message_id}',
    response_model=MessageRead,
    status_code=status.HTTP_200_OK,
    name='delete_message',
)
async def delete_message(
    message_id: int,
    repository: MessageRepository = Depends(get_repository(MessageRepository)),
    user: User = Depends(get_current_user),
) -> None:
    try:
        await repository.get(model_id=message_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Message with ID={message_id} not found'
        )
    return await repository.delete(model_id=message_id)
