from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from db.errors import EntityDoesNotExist
from db.sessions import get_repository
from routers.users import get_current_user
from schemas.tags import Tag, TagCreate, TagRead, TagUpdate
from repositories.tags import TagRepository
from schemas.users import User

router = APIRouter(prefix='/tags')


@router.put(
    '/{tag_id}',
    response_model=TagRead,
    status_code=status.HTTP_200_OK,
    name='update_tag',
)
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate = Body(...),
    repository: TagRepository = Depends(get_repository(TagRepository)),
    user: User = Depends(get_current_user),
) -> TagRead:
    try:
        await repository.get(model_id=tag_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Tag with ID={tag_id} not found'
        )
    return await repository.update(model_id=tag_id, model_update=tag_update)


@router.delete(
    '/{tag_id}',
    status_code=status.HTTP_200_OK,
    name='delete_tag',
)
async def delete_tag(
    tag_id: int,
    repository: TagRepository = Depends(get_repository(TagRepository)),
    user: User = Depends(get_current_user),
) -> None:
    try:
        await repository.get(model_id=tag_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Tag with ID={tag_id} not found'
        )
    return await repository.delete(model=Tag, model_id=tag_id)
