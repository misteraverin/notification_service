from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlmodel import select

from db.errors import EntityDoesNotExist
from repositories.base import BaseRepository
from schemas.base import StatusEnum, TimeStampModel
from schemas.customers import Customer
from schemas.mailouts import Mailout
from schemas.messages import Message, MessageCreate, MessageRead, MessageUpdate


class MessageRepository(BaseRepository):
    model = Message

    async def create(self, model_create: MessageCreate) -> MessageRead:
        customer_query = await self.session.exec(
            select(Customer)
            .where(Customer.id == model_create.customer_id)
        )
        customer = customer_query.first()
        mailout_query = await self.session.exec(
            select(Mailout)
            .where(Mailout.id == model_create.mailout_id)
        )
        mailout = mailout_query.first()

        if not customer or not mailout:
            raise EntityDoesNotExist
        else:
            return await self._create_not_unique(self.model, model_create)

    async def list(self, limit: int = 50, offset: int = 0) -> list[MessageRead]:
        return await super().list(self.model, limit, offset)

    async def get(self, model_id: int) -> Optional[MessageRead]:
        return await super().get(self.model, model_id)

    async def update(self, model_id: int, model_update: MessageUpdate) -> Optional[MessageRead]:
        if item := await self._get_instance(self.model, model_id):
            item_dict = model_update.dict(
                exclude_unset=True,
                exclude={'id', 'status', 'created_at'},
            )
            for key, value in item_dict.items():
                setattr(item, key, value)

            if not model_update.status:
                setattr(item, 'status', StatusEnum.updated)
            else:
                setattr(item, 'status', model_update.status)
            setattr(item, 'created_at', datetime.utcnow())

            await self._add_to_db(item)
            return await self._get_instance(self.model, model_id)
        else:
            raise EntityDoesNotExist

    async def delete(self, model_id: int) -> None:
        if item := await self._get_instance(self.model, model_id):
            setattr(item, 'status', StatusEnum.deleted)
            await self._add_to_db(item)
            return await self._get_instance(self.model, model_id)
        else:
            raise EntityDoesNotExist

    async def delete_model_tag(self, model, model_id: int, tag_model, tag_id: int):
        raise NotImplementedError

    async def delete_model_phone_code(self, model, model_id: int, phone_code_model, phone_code_id: int):
        raise NotImplementedError

    async def get_general_stats(self):
        query = (
            select(
                self.model.status.label('status'),
                func.count(self.model.id).label('count')
            )
            .group_by(self.model.status)
            .order_by(func.count(self.model.id).desc())
        )
        results = await self.session.exec(query)
        return results.all()

    async def get_detailed_stats(self, model_id: int, status: StatusEnum = None):
        query = (
            select(
                self.model.status.label('status'),
                func.count(self.model.id).label('count')
            )
            .where(self.model.mailout_id == model_id)
        )

        if status:
            query = query.where(self.model.status == status)

        query = (
            query
            .group_by(self.model.status)
            .order_by(func.count(self.model.id).desc())
        )

        results = await self.session.exec(query)
        return results.all()

    async def start_mailout(self, model_id: int):
        instance = await self._get_instance(self.model, model_id)
        if instance:
            process_mailout.delay(instance.id)
            result = f'Mailout {instance.id} set to processing'
            logger.info(result)
            return result
        else:
            raise EntityDoesNotExist
