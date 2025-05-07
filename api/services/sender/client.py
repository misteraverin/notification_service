from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import requests

from utils.logging import logger


@dataclass
class MailoutMessage:
    id: int
    phone: str
    text: str

    def as_dict(self):
        return asdict(self)


class ClientInterface(ABC):
    @abstractmethod
    def send_mailout(self, message: MailoutMessage) -> (int, str):
        pass


class Client(ClientInterface):
    api_base_url = 'https://probe.fbrq.cloud/v1/send'
    api_token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDI0NjIzNDYsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6ImRtaX'
        'RyeV92X2thcnBvdiJ9.wUsnGQVcNN2wi_cnLIszNmYnVokzuGICk6dL3ePteNg'
    )
    api_auth_header_prefix = 'Bearer'
    api_auth_header = 'Authorization'

    def __init__(self, *args, **kwargs):
        session = requests.Session()
        session.headers.update({self.api_auth_header: f'{self.api_auth_header_prefix} {self.api_token}'})
        self._session = session
        super().__init__(*args, **kwargs)

    def send_mailout(self, message: MailoutMessage) -> (int, str):
        api_url = f'{self.api_base_url}/{message.id}'
        try:
            resp = self._session.post(api_url, json=message.as_dict())
            return resp.status_code, resp.text
        except (requests.ConnectionError, requests.ConnectTimeout, Exception) as err:
            err = f'[msg {message.id}] querying url "{api_url}" resulted in an error: {str(err)}'
            logger.error(err)
            return 500, err


if __name__ == '__main__':
    Client().send_mailout(
        MailoutMessage(
            id=1,
            phone='79201234567',
            text='API client testing',
        )
    )
