from __future__ import absolute_import

import os
from dotenv import load_dotenv

import asyncio
from celery import Celery
from celery.schedules import crontab

from services.sender.mailout import MailoutService

load_dotenv()

celery_app = Celery(
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379'),
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['application/json'],
    result_serializer='json',
    beat_schedule={
        'send-messages-scheduled-task': {
            'task': 'services.sender.celery_worker.process_mailouts',
            'schedule': crontab(minute='*/1')
        }
    },
    task_routes={
        'services.sender.celery_worker.process_mailouts': 'main-queue',
        'services.sender.celery_worker.process_mailout': 'main-queue',
    },
)


@celery_app.task
def process_mailouts():
    asyncio.get_event_loop().run_until_complete(MailoutService().process_mailouts())


@celery_app.task
def process_mailout(mailout_id: int):
    asyncio.get_event_loop().run_until_complete(MailoutService().process_mailout(mailout_id))
