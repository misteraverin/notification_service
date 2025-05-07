from typing import Optional
import zoneinfo

from sqlalchemy import select

from db.errors import TimezoneError
from repositories.base import BaseRepository
from schemas.timezones import Timezone, TimezoneCreate, TimezoneRead, TimezoneUpdate


class TimezoneRepository(BaseRepository):
    model = Timezone

    async def create(self, model_create: TimezoneCreate) -> TimezoneRead:
        if model_create.timezone not in zoneinfo.available_timezones():
            raise TimezoneError
        query = select(self.model).where(self.model.timezone == model_create.timezone)
        result = await self._upsert(query, self.model, model_create)
        await self._add_to_db(result)
        return result

    async def list(self, limit: int = 50, offset: int = 0) -> list[TimezoneRead]:
        return await super().list(self.model, limit, offset)

    async def get(self, model_id: int) -> Optional[TimezoneRead]:
        return await super().get(self.model, model_id)

    async def update(self, model_id: int, model_update: TimezoneUpdate) -> Optional[TimezoneRead]:
        if model_update.timezone not in zoneinfo.available_timezones():
            raise TimezoneError
        return await super().update(self.model, model_id, model_update)

    async def delete_model_tag(self, model, model_id: int, tag_model, tag_id: int):
        raise NotImplementedError

    async def delete_model_phone_code(self, model, model_id: int, phone_code_model, phone_code_id: int):
        raise NotImplementedError
