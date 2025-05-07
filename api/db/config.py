import os

from dotenv import load_dotenv
from pydantic import BaseConfig

load_dotenv()


class Settings(BaseConfig):
    title: str = os.environ.get("TITLE", "Default API Title")
    version: str = "1.0.0"
    description: str = os.environ.get("DESCRIPTION", "Default API Description")
    openapi_prefix: str = os.environ.get("OPENAPI_PREFIX", "")
    redoc_url: str = os.environ.get("REDOC_URL", "/redoc")
    openapi_url: str = os.environ.get("OPENAPI_URL", "/openapi.json")
    docs_url: str = os.environ.get("DOCS_URL", "/docs")
    api_prefix: str = os.environ.get("API_PREFIX", "/api")
    debug: bool = os.environ.get("DEBUG", "False").lower() == "true"
    postgres_user: str = os.environ.get("POSTGRES_USER", "user")
    postgres_password: str = os.environ.get("POSTGRES_PASSWORD", "password")
    postgres_server: str = os.environ.get("POSTGRES_SERVER", "localhost")
    postgres_port: str = os.environ.get("POSTGRES_PORT", "5432")
    postgres_db: str = os.environ.get("POSTGRES_DB", "app_db")
    postgres_db_tests: str = os.environ.get("POSTGRES_DB_TESTS", "test_db")
    db_echo_log: bool = (
        True if os.environ.get("DB_ECHO_LOG", "False").lower() == "true" else False
    )

    class Config:
        env_file = ".env"

    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
