from abc import ABC, abstractmethod
from datetime import datetime
import time

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.errors import EntityDoesNotExist
from db.sessions import async_engine
from repositories.phone_codes import PhoneCodeRepository
from repositories.mailouts import MailoutRepository
from repositories.messages import MessageRepository
from schemas.link_schemas import CustomerTag
from schemas.tags import Tag
from schemas.mailouts import Mailout
from schemas.customers import Customer
from schemas.messages import MessageCreate, MessageUpdate
from schemas.base import StatusEnum
from services.sender.client import Client, ClientInterface, MailoutMessage
from services.sender.metrics import messages_total_sent, messages_total_failed
from utils.logging import logger


class MailoutServiceInterface(ABC):
    _fbrq_client: ClientInterface

    def __init__(self):
        self._fbrq_client = Client()

    @abstractmethod
    def process_mailouts(self) -> None:
        pass

    @abstractmethod
    def process_mailout(self, mailout_id: int) -> None:
        pass


class MailoutService(MailoutServiceInterface):
    _mailout_send_max_tries: int = 3

    async def process_mailouts(self) -> None:
        async with AsyncSession(async_engine) as async_session:
            mailout_repository = MailoutRepository(async_session)

            logger.info(f'Processing jobs (mailouts) by scheduler')
            jobs = await mailout_repository.select_mailout_jobs()
            job_count = len(jobs)
            logger.info(f'Total of {job_count} jobs are available for processing')

            if not job_count:
                return

            for job in jobs:
                await self._process_mailout(job)

    async def process_mailout(self, mailout_id: int) -> None:
        async with AsyncSession(async_engine) as async_session:
            mailout_repository = MailoutRepository(async_session)

            try:
                instance = await mailout_repository.get(model_id=mailout_id)
            except EntityDoesNotExist:
                logger.info(f'Job {mailout_id} not found')
                return

            await self._process_mailout(instance)

    async def _process_mailout(self, mailout: Mailout) -> None:
        async with AsyncSession(async_engine) as async_session:
            job_id = mailout.id
            logger.info(f'Processing job (mailout) {job_id}')

            if not mailout.requires_processing():
                logger.info(f'Job {job_id} does not need processing')
                return

            query = (
                select(Customer)
                .join(CustomerTag, Customer.id == CustomerTag.customer_id)
                .join(Tag, Tag.id == CustomerTag.tag_id)
                .where(Tag.tag.in_([m.tag for m in mailout.tags]))
            )

            results = await async_session.exec(query)
            customers = results.all()

            job_customer_count = len(customers)
            logger.info(f'Job {job_id} has total of {job_customer_count} customers to notify')

            if not job_customer_count:
                return

            job_processed_customer_count = 0
            for customer in customers:
                if datetime.utcnow() >= mailout.finish_at:
                    logger.info(
                        f"Job {job_id} has expired, total job's customers (messages) "
                        f"processed: {job_processed_customer_count}"
                    )
                    return

                job_processed_customer_count += 1
                await self._process_customer_mailout(mailout=mailout, customer=customer)

            logger.info(f'Job {job_id} total customers (messages) processed: {job_processed_customer_count}')

    async def _process_customer_mailout(self, mailout: Mailout, customer: Customer) -> None:
        async with AsyncSession(async_engine) as async_session:
            message_repository = MessageRepository(async_session)
            phone_code_repository = PhoneCodeRepository(async_session)

            msg = await message_repository.create(
                model_create=MessageCreate(
                    status=StatusEnum.pending,
                    mailout_id=mailout.id,
                    customer_id=customer.id,
                )
            )

            job_id = mailout.id
            logger.info(f'Job: {job_id}, customer: {customer.id}, processing message: {msg.id}')
            phone_code = await phone_code_repository.get(model_id=customer.phone_code_id)
            phone = f'{customer.country_code}{phone_code.phone_code}{customer.phone}'
            client_msg = MailoutMessage(id=msg.id, phone=phone, text=mailout.text_message)

            for current_try_number in range(self._mailout_send_max_tries):
                logger.info(f'Trying to send message {msg.id} for a try No. {current_try_number + 1}')
                status, _ = self._fbrq_client.send_mailout(client_msg)
                if status == 200:
                    await message_repository.update(
                        model_id=msg.id,
                        model_update=MessageUpdate(
                            status=StatusEnum.sent,
                            mailout_id=mailout.id,
                            customer_id=customer.id,
                        )
                    )
                    logger.info(f'Message {msg.id} successfully sent on a try No. {current_try_number + 1}')
                    messages_total_sent.inc()
                    return

                time.sleep(0.5)

            logger.info(f'Failed to send message {msg.id} after {self._mailout_send_max_tries} tries')
            await message_repository.update(
                model_id=msg.id,
                model_update=MessageUpdate(
                    status=StatusEnum.failed,
                    mailout_id=mailout.id,
                    customer_id=customer.id,
                )
            )
            messages_total_failed.inc()
