from datetime import datetime
from typing import Optional

from sqlmodel import select

from db.errors import EntityDoesNotExist, WrongDatetimeError
from repositories.base import BaseRepository
from schemas.phone_codes import PhoneCode
from schemas.tags import Tag
from schemas.mailouts import Mailout, MailoutRead, MailoutCreate, MailoutUpdate
from services.sender.metrics import mailouts_total_created


def check_time(model):
    if (
        model.start_at > model.finish_at
        or model.available_start_at > model.available_finish_at
    ):
        raise WrongDatetimeError


class MailoutRepository(BaseRepository):
    model = Mailout

    async def create(self, model_create: MailoutCreate) -> MailoutRead:
        check_time(model_create)
        mailouts_total_created.inc()
        return await self._create_not_unique(self.model, model_create)

    async def list(
        self,
        limit: int = 50,
        tag: Optional[list[str]] = None,
        phone_code: Optional[list[str]] = None,
        offset: int = 0,
    ) -> list[MailoutRead]:
        query = select(self.model).order_by(self.model.id)
        if tag:
            query = query.where(self.model.tags.any(Tag.tag.in_(tag)))
        if phone_code:
            query = query.where(self.model.phone_codes.any(PhoneCode.phone_code.in_(phone_code)))
        query = query.offset(offset).limit(limit)
        return await self.get_list(query)

    async def get(self, model_id: int) -> Optional[MailoutRead]:
        return await super().get(self.model, model_id)

    async def update(self, model_id: int, model_update: MailoutUpdate) -> Optional[MailoutRead]:
        check_time(model_update)
        return await super().update(self.model, model_id, model_update)

    async def delete_mailout_tag(self, model_id: int, tag_id: int) -> Optional[MailoutRead]:
        return await super().delete_model_tag(self.model, model_id, Tag, tag_id)

    async def delete_mailout_phone_code(self, model_id: int, phone_code_id: int) -> Optional[MailoutRead]:
        return await super().delete_model_phone_code(self.model, model_id, PhoneCode, phone_code_id)

    async def select_mailout_jobs(self):
        _now = datetime.now()
        query = (
            select(self.model)
            .where(self.model.start_at <= _now)
            .where(self.model.finish_at > _now)
        )
        return await self.get_list(query)

    async def delete_model_tag(self, model, model_id: int, tag_model, tag_id: int):
        raise NotImplementedError

    async def delete_model_phone_code(self, model, model_id: int, phone_code_model, phone_code_id: int):
        raise NotImplementedError
