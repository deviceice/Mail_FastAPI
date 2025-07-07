from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from pydantic_core import MultiHostUrl

from mail.settings_mail_servers.settings_server import SettingsServer


def asyncpg_url() -> MultiHostUrl:
    try:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=SettingsServer.DB_USER,
            password=SettingsServer.DB_PASS,
            host=SettingsServer.DB_IP,
            port=SettingsServer.DB_PORT,
            path=SettingsServer.DB_NAME,
        )
    except KeyError as e:
        logger.error(f"Отсутствует ключ в конфигурации БД: {e}")
        raise ValueError(f"Invalid database configuration: {e}") from e


class AsyncDB:
    def __init__(self):
        self.engine = None
        self.AsyncSessionFactory = None

    async def create_eng_session(self):
        await self.create_engine()
        await self.create_async_sessionmaker()

    async def create_engine(self):
        self.engine = create_async_engine(asyncpg_url().unicode_string(),
                                          pool_size=30,
                                          max_overflow=50,
                                          pool_pre_ping=True,
                                          future=True,
                                          echo=False)

    async def create_async_sessionmaker(self):
        self.AsyncSessionFactory = async_sessionmaker(
            self.engine,
            autoflush=True,
            expire_on_commit=False,
        )

    async def get_engine(self):
        return self.engine

    async def get_asyncSessionFactory(self):
        return self.AsyncSessionFactory
