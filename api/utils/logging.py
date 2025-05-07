from __future__ import absolute_import

from json.decoder import JSONDecodeError
import logging
from logging.handlers import TimedRotatingFileHandler
import os

import celery
from fastapi import Request


@celery.signals.setup_logging.connect
def on_setup_logging(**kwargs):
    pass


class LoggerConfig:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logfile = os.path.join('utils/logs/log_file.log')

        self.handler_cmdline = logging.StreamHandler()
        self.handler_file = TimedRotatingFileHandler(
            filename=self.logfile,
            when='H',
            backupCount=1,
        )
        self.handler_cmdline.setLevel(logging.INFO)
        self.handler_file.setLevel(logging.INFO)

        log_format = logging.Formatter(
            '{'
            '\n\t"time": "%(asctime)s",\n'
            '\t"name": "%(name)s",\n'
            '\t"level": "%(levelname)s",\n'
            '\t"message": "%(message)s"\n'
            '},'
        )
        self.handler_cmdline.setFormatter(log_format)
        self.handler_file.setFormatter(log_format)

        self.logger.addHandler(self.handler_cmdline)
        self.logger.addHandler(self.handler_file)
        self.logger.setLevel(logging.INFO)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)


logger = LoggerConfig()


async def log_request_info(request: Request):
    try:
        request_body = await request.json()
    except JSONDecodeError:
        request_body = {}

    logger.info(
        '{'
        f'\n\t\t"method": "{request.method}",\n'
        f'\t\t"url": "{request.url}",\n'
        f'\t\t"headers": {dict(request.headers)},\n'
        f'\t\t"body": {request_body},\n'
        f'\t\t"path_params": {request.path_params},\n'
        f'\t\t"query_params": "{request.query_params}",\n'
        f'\t\t"cookies": {request.cookies}\n'
        '\t}'
    )
