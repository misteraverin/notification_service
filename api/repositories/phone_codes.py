import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.errors import EntityDoesNotExist, PhoneCodeError
from repositories.base import BaseRepository
from schemas.phone_codes import PhoneCode, PhoneCodeCreate, PhoneCodeRead, PhoneCodeUpdate


def check_phone_code(phone_code):
    regex = r'^[0-9]{3}$'
    if not re.search(regex, phone_code, re.I):
        raise PhoneCodeError


class PhoneCodeRepository(BaseRepository):
    model = PhoneCode

    async def create(
        self,
        model_create: PhoneCodeCreate,
        parent_model=None,
        model_id=None,
    ) -> PhoneCodeRead:
        check_phone_code(model_create.phone_code)

        phone_code_query = (
            select(self.model)
            .where(self.model.phone_code == model_create.phone_code)
        )
        result = await self._upsert(phone_code_query, self.model, model_create)
        self.session.add(result)

        if parent_model:
            model_query = await self.session.scalars(
                select(parent_model)
                .where(parent_model.id == model_id)
                .options(selectinload(parent_model.phone_codes))
            )
            if item := model_query.first():
                item.phone_codes.append(result)
            else:
                raise EntityDoesNotExist

        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def list(self, limit: int = 50, offset: int = 0) -> list[PhoneCodeRead]:
        return await super().list(self.model, limit, offset)

    async def get(self, model_id: int) -> Optional[PhoneCodeRead]:
        return await super().get(self.model, model_id)

    async def update(self, model_id: int, model_update: PhoneCodeUpdate) -> Optional[PhoneCodeRead]:
        check_phone_code(model_update.phone_code)
        return await super().update(self.model, model_id, model_update)

    async def delete_model_tag(self, model, model_id: int, tag_model, tag_id: int):
        raise NotImplementedError

    async def delete_model_phone_code(self, model, model_id: int, phone_code_model, phone_code_id: int):
        raise NotImplementedError
