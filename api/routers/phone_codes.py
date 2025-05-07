from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from db.errors import EntityDoesNotExist
from db.sessions import get_repository
from repositories.phone_codes import PhoneCodeRepository
from routers.users import get_current_user
from schemas.phone_codes import PhoneCode, PhoneCodeCreate, PhoneCodeRead, PhoneCodeUpdate
from schemas.users import User

router = APIRouter(prefix='/phone_codes')


@router.post(
    '/',
    response_model=PhoneCodeRead,
    status_code=status.HTTP_201_CREATED,
    name='create_phone_code',
)
async def create_phone_code(
    phone_code_create: PhoneCodeCreate = Body(...),
    repository: PhoneCodeRepository = Depends(get_repository(PhoneCodeRepository)),
    user: User = Depends(get_current_user),
) -> PhoneCodeRead:
    return await repository.create(model_create=phone_code_create)


@router.get(
    '/',
    response_model=list[Optional[PhoneCodeRead]],
    status_code=status.HTTP_200_OK,
    name='get_phone_codes',
)
async def get_phone_codes(
    limit: int = Query(default=50, lte=100),
    offset: int = Query(default=0),
    repository: PhoneCodeRepository = Depends(get_repository(PhoneCodeRepository))
) -> list[Optional[PhoneCodeRead]]:
    return await repository.list(
        limit=limit,
        offset=offset,
    )


@router.get(
    '/{phone_code_id}',
    response_model=PhoneCodeRead,
    status_code=status.HTTP_200_OK,
    name='get_phone_code',
)
async def get_phone_code(
    phone_code_id: int,
    repository: PhoneCodeRepository = Depends(get_repository(PhoneCodeRepository)),
) -> PhoneCodeRead:
    try:
        result = await repository.get(model_id=phone_code_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Phone code with ID={phone_code_id} not found'
        )
    return result


@router.put(
    '/{phone_code_id}',
    response_model=PhoneCodeRead,
    status_code=status.HTTP_200_OK,
    name='update_phone_code',
)
async def update_phone_code(
    phone_code_id: int,
    phone_code_update: PhoneCodeUpdate = Body(...),
    repository: PhoneCodeRepository = Depends(get_repository(PhoneCodeRepository)),
    user: User = Depends(get_current_user),
) -> PhoneCodeRead:
    try:
        await repository.get(model_id=phone_code_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Phone code with ID={phone_code_id} not found'
        )
    return await repository.update(
        model_id=phone_code_id, model_update=phone_code_update
    )


@router.delete(
    '/{phone_code_id}',
    status_code=status.HTTP_200_OK,
    name='delete_phone_code',
)
async def delete_phone_code(
    phone_code_id: int,
    repository: PhoneCodeRepository = Depends(get_repository(PhoneCodeRepository)),
    user: User = Depends(get_current_user),
) -> None:
    try:
        await repository.get(model_id=phone_code_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Phone code with ID={phone_code_id} not found'
        )
    return await repository.delete(model=PhoneCode, model_id=phone_code_id)
