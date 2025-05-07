from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from db.errors import EntityDoesNotExist


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_instance(self, model, model_id: int):
        query = select(model).where(model.id == model_id)
        result = await self.session.scalars(query.options(selectinload('*')))
        return result.first()

    async def get_list(self, query):
        results = await self.session.exec(query.options(selectinload('*')))
        try:
            return results.scalars().all()
        except AttributeError:
            return results.all()

    async def _add_to_db(self, new_item):
        self.session.add(new_item)
        await self.session.commit()
        await self.session.refresh(new_item)

    async def _upsert(self, query, model, model_create):
        result = await self.session.exec(query)
        result = result.scalars().first()
        model_from_orm = model.from_orm(model_create)

        if result is None:
            result = model_from_orm

        for k, v in model_from_orm.dict(exclude_unset=True).items():
            setattr(result, k, v)

        return result

    async def _create_not_unique(self, model, model_create):
        new_item = model.from_orm(model_create)
        await self._add_to_db(new_item)
        return await self._get_instance(model, new_item.id)

    async def list(self, model, limit: int = 50, offset: int = 0):
        query = select(model).order_by(model.id).offset(offset).limit(limit)
        return await self.get_list(query)

    async def get(self, model, model_id: int):
        if item := await self._get_instance(model, model_id):
            return item
        else:
            raise EntityDoesNotExist

    async def update(self, model, model_id: int, model_update):
        if item := await self._get_instance(model, model_id):
            item_dict = model_update.dict(
                exclude_unset=True,
                exclude={'id'},
            )
            for key, value in item_dict.items():
                setattr(item, key, value)
            await self._add_to_db(item)
            return await self._get_instance(model, model_id)
        else:
            raise EntityDoesNotExist

    async def delete(self, model, model_id: int) -> None:
        if item := await self._get_instance(model, model_id):
            await self.session.delete(item)
            await self.session.commit()
        else:
            raise EntityDoesNotExist

    async def delete_model_tag(self, model, model_id: int, tag_model, tag_id: int):
        tag_to_delete = await self._get_instance(tag_model, tag_id)
        instance = await self._get_instance(model, model_id)

        if instance and (tag_to_delete in instance.tags):
            instance.tags.remove(tag_to_delete)
            await self._add_to_db(instance)
            return await self._get_instance(model, model_id)
        else:
            raise EntityDoesNotExist

    async def delete_model_phone_code(self, model, model_id: int, phone_code_model, phone_code_id: int):
        phone_code_to_delete = await self._get_instance(phone_code_model, phone_code_id)
        instance = await self._get_instance(model, model_id)

        if instance and (phone_code_to_delete in instance.phone_codes):
            instance.phone_codes.remove(phone_code_to_delete)
            await self._add_to_db(instance)
            return await self._get_instance(model, model_id)
        else:
            raise EntityDoesNotExist
