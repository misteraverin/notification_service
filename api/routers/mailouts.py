from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from db.errors import EntityDoesNotExist
from db.sessions import get_repository
from repositories.phone_codes import PhoneCodeRepository
from repositories.tags import TagRepository
from repositories.mailouts import MailoutRepository
from routers.users import get_current_user
from schemas.phone_codes import PhoneCode, PhoneCodeCreate, PhoneCodeRead, PhoneCodeUpdate
from schemas.tags import Tag, TagCreate, TagRead, TagUpdate
from schemas.mailouts import Mailout, MailoutCreate, MailoutRead, MailoutUpdate
from schemas.users import User
from services.sender.celery_worker import process_mailout
from utils.logging import logger

router = APIRouter(prefix='/mailouts')


@router.post(
    '/',
    response_model=MailoutRead,
    status_code=status.HTTP_201_CREATED,
    name='create_mailout',
)
async def create_mailout(
    mailout_create: MailoutCreate = Body(...),
    repository: MailoutRepository = Depends(get_repository(MailoutRepository)),
    user: User = Depends(get_current_user),
) -> MailoutRead:
    return await repository.create(model_create=mailout_create)


@router.get(
    '/',
    response_model=list[Optional[MailoutRead]],
    status_code=status.HTTP_200_OK,
    name='get_mailouts',
)
async def get_mailouts(
    tag: Optional[list[str]] = Query(default=None),
    phone_code: Optional[list[str]] = Query(default=None),
    limit: int = Query(default=50, lte=100),
    offset: int = Query(default=0),
    repository: MailoutRepository = Depends(get_repository(MailoutRepository))
) -> list[Optional[MailoutRead]]:
    return await repository.list(
        tag=tag,
        phone_code=phone_code,
        limit=limit,
        offset=offset,
    )


@router.get(
    '/{mailout_id}',
    response_model=MailoutRead,
    status_code=status.HTTP_200_OK,
    name='get_mailout',
)
async def get_mailout(
    mailout_id: int,
    repository: MailoutRepository = Depends(get_repository(MailoutRepository)),
) -> MailoutRead:
    try:
        result = await repository.get(model_id=mailout_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Mailout with ID={mailout_id} not found'
        )
    return result


@router.put(
    '/{mailout_id}',
    response_model=MailoutRead,
    status_code=status.HTTP_200_OK,
    name='update_mailout',
)
async def update_mailout(
    mailout_id: int,
    mailout_update: MailoutUpdate = Body(...),
    repository: MailoutRepository = Depends(get_repository(MailoutRepository)),
    user: User = Depends(get_current_user),
) -> MailoutRead:
    try:
        await repository.get(model_id=mailout_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Mailout with ID={mailout_id} not found'
        )
    return await repository.update(model_id=mailout_id, model_update=mailout_update)


@router.delete(
    '/{mailout_id}',
    status_code=status.HTTP_200_OK,
    name='delete_mailout',
)
async def delete_mailout(
    mailout_id: int,
    repository: MailoutRepository = Depends(get_repository(MailoutRepository)),
    user: User = Depends(get_current_user),
) -> None:
    try:
        await repository.get(model_id=mailout_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Mailout with ID={mailout_id} not found'
        )
    return await repository.delete(model=Mailout, model_id=mailout_id)


@router.post(
    '/{mailout_id}/tags',
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    name='create_mailout_tag',
)
async def create_mailout_tag(
    mailout_id: int,
    tag_create: TagCreate = Body(...),
    repository: TagRepository = Depends(get_repository(TagRepository)),
    user: User = Depends(get_current_user),
) -> TagRead:
    try:
        return await repository.create(
            model_id=mailout_id,
            tag_create=tag_create,
            parent_model=Mailout,
        )
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Mailout with ID={mailout_id} not found'
        )


@router.post(
    '/{mailout_id}/phone_codes',
    response_model=PhoneCodeRead,
    status_code=status.HTTP_201_CREATED,
    name='create_mailout_phone_code',
)
async def create_mailout_phone_code(
    mailout_id: int,
    phone_code_create: PhoneCodeCreate = Body(...),
    repository: PhoneCodeRepository = Depends(get_repository(PhoneCodeRepository)),
    user: User = Depends(get_current_user),
) -> PhoneCodeRead:
    try:
        return await repository.create(
            model_id=mailout_id,
            model_create=phone_code_create,
            parent_model=Mailout,
        )
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Mailout with ID={mailout_id} not found'
        )


@router.post(
    '/{mailout_id}/tags/{tag_id}',
    response_model=MailoutRead,
    status_code=status.HTTP_200_OK,
    name='delete_mailout_tag',
)
async def delete_mailout_tag(
    mailout_id: int,
    tag_id: int,
    repository: MailoutRepository = Depends(get_repository(MailoutRepository)),
    user: User = Depends(get_current_user),
) -> MailoutRead:
    try:
        return await repository.delete_mailout_tag(tag_id=tag_id, model_id=mailout_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Mailout or tag not found'
        )


@router.post(
    '/{mailout_id}/phone_codes/{phone_code_id}',
    response_model=MailoutRead,
    status_code=status.HTTP_200_OK,
    name='delete_mailout_phone_code',
)
async def delete_mailout_phone_code(
    mailout_id: int,
    phone_code_id: int,
    repository: MailoutRepository = Depends(get_repository(MailoutRepository)),
    user: User = Depends(get_current_user),
) -> MailoutRead:
    try:
        return await repository.delete_mailout_phone_code(
            phone_code_id=phone_code_id, model_id=mailout_id
        )
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Mailout or phone code not found'
        )


@router.get(
    '/{mailout_id}/start',
    status_code=status.HTTP_200_OK,
    name='start_mailout',
)
async def start_mailout(
    mailout_id: int,
    repository: MailoutRepository = Depends(get_repository(MailoutRepository)),
    user: User = Depends(get_current_user),
):
    try:
        instance = await repository.get(mailout_id)
        process_mailout.delay(instance.id)
        result = f'Mailout {instance.id} set to processing'
        logger.info(result)
        return result
    except EntityDoesNotExist:
        logger.info(f'Mailout with ID={mailout_id} not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Mailout with ID={mailout_id} not found'
        )
