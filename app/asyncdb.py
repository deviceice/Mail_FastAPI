from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from pydantic_core import MultiHostUrl
from config import Settings

settings = Settings()


def asyncpg_url(header_name_in_config) -> MultiHostUrl:
    settings.open_conf()
    config = settings.get_conf()
    try:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=config[header_name_in_config]['user'],
            password=config[header_name_in_config]['password'],
            host=config[header_name_in_config]['ip_db'],
            port=int(config[header_name_in_config]['port_db']),
            path=config[header_name_in_config]['name_db'],
        )
    except KeyError as e:
        logger.error(f"Отсутствует ключ в конфигурации: {e}")
        raise ValueError(f"Invalid database configuration: {e}") from e


class AsyncDB:
    def __init__(self):
        self.engine = None
        self.AsyncSessionFactory = None

    async def create_eng_session(self, header_name_in_config):
        await self.create_engine(header_name_in_config)
        await self.create_async_sessionmaker()

    async def create_engine(self, header_name_in_config):
        self.engine = create_async_engine(asyncpg_url(header_name_in_config).unicode_string(),
                                          pool_size=20,
                                          max_overflow=0,
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
