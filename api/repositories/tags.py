from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.errors import EntityDoesNotExist
from repositories.base import BaseRepository
from schemas.tags import Tag, TagCreate, TagRead, TagUpdate


class TagRepository(BaseRepository):
    model = Tag

    async def create(self, model_id: int, tag_create: TagCreate, parent_model) -> TagRead:
        model_query = await self.session.scalars(
            select(parent_model)
            .where(parent_model.id == model_id)
            .options(selectinload(parent_model.tags))
        )
        if item := model_query.first():
            tag_query = select(self.model).where(self.model.tag == tag_create.tag)
            new_tag = await self._upsert(tag_query, Tag, tag_create)
            self.session.add(new_tag)
            item.tags.append(new_tag)
            await self.session.commit()
            await self.session.refresh(new_tag)
            return new_tag
        else:
            raise EntityDoesNotExist

    async def get(self, model_id: int) -> Optional[TagRead]:
        return await super().get(self.model, model_id)

    async def update(self, model_id: int, model_update: TagUpdate) -> Optional[TagRead]:
        return await super().update(self.model, model_id, model_update)

    async def delete_model_tag(self, model, model_id: int, tag_model, tag_id: int):
        raise NotImplementedError

    async def delete_model_phone_code(self, model, model_id: int, phone_code_model, phone_code_id: int):
        raise NotImplementedError
