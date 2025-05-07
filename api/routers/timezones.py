from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from db.errors import EntityDoesNotExist
from db.sessions import get_repository
from repositories.timezones import TimezoneRepository
from routers.users import get_current_user
from schemas.timezones import Timezone, TimezoneCreate, TimezoneRead, TimezoneUpdate
from schemas.users import User

router = APIRouter(prefix='/timezones')


@router.post(
    '/',
    response_model=TimezoneRead,
    status_code=status.HTTP_201_CREATED,
    name='create_timezone',
)
async def create_timezone(
    timezone_create: TimezoneCreate = Body(...),
    repository: TimezoneRepository = Depends(get_repository(TimezoneRepository)),
    user: User = Depends(get_current_user),
) -> TimezoneRead:
    return await repository.create(model_create=timezone_create)


@router.get(
    '/',
    response_model=list[Optional[TimezoneRead]],
    status_code=status.HTTP_200_OK,
    name='get_timezones',
)
async def get_timezones(
    limit: int = Query(default=50, lte=100),
    offset: int = Query(default=0),
    repository: TimezoneRepository = Depends(get_repository(TimezoneRepository))
) -> list[Optional[TimezoneRead]]:
    return await repository.list(limit=limit, offset=offset)


@router.get(
    '/{timezone_id}',
    response_model=TimezoneRead,
    status_code=status.HTTP_200_OK,
    name='get_timezone',
)
async def get_timezone(
    timezone_id: int,
    repository: TimezoneRepository = Depends(get_repository(TimezoneRepository)),
) -> TimezoneRead:
    try:
        result = await repository.get(model_id=timezone_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Timezone with ID={timezone_id} not found'
        )
    return result


@router.put(
    '/{timezone_id}',
    response_model=TimezoneRead,
    status_code=status.HTTP_200_OK,
    name='update_timezone',
)
async def update_timezone(
    timezone_id: int,
    timezone_update: TimezoneUpdate = Body(...),
    repository: TimezoneRepository = Depends(get_repository(TimezoneRepository)),
    user: User = Depends(get_current_user),
) -> TimezoneRead:
    try:
        await repository.get(model_id=timezone_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Timezone with ID={timezone_id} not found'
        )
    return await repository.update(model_id=timezone_id, model_update=timezone_update)


@router.delete(
    '/{timezone_id}',
    status_code=status.HTTP_200_OK,
    name='delete_timezone',
)
async def delete_timezone(
    timezone_id: int,
    repository: TimezoneRepository = Depends(get_repository(TimezoneRepository)),
    user: User = Depends(get_current_user),
) -> None:
    try:
        await repository.get(model_id=timezone_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Timezone with ID={timezone_id} not found'
        )
    return await repository.delete(model=Timezone, model_id=timezone_id)
