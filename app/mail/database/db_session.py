from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.schema import CreateSchema
from mail.database.models_mail import *
from loguru import logger
from asyncdb import AsyncDB

async_db_mail = AsyncDB()


@asynccontextmanager
async def get_session() -> AsyncGenerator:
    try:
        async with async_db_mail.AsyncSessionFactory() as session:
            logger.info(f"ASYNC Pool mail: {async_db_mail.engine.pool.status()}")
            try:
                yield session
            except Exception as e:
                logger.error(f"Ошибка session_db mail: {e}")
                raise
    except Exception as e:
        logger.critical(f"Не удалось подключиться к DB mail:{e}")
        yield session


async def create_tables_mail():
    async with async_db_mail.engine.begin() as conn:
        try:
            await conn.execute(CreateSchema('mail'))
            logger.success('Схема для mail успешно создана!')
        except sqlalchemy.exc.ProgrammingError:
            pass
            # logger.success("Схема для mail уже существует в БД")
        try:
            await conn.run_sync(Base.metadata.create_all)
            # await conn.run_sync(Base.metadata)
            logger.success("Таблицы для mail успешно созданы")
        except sqlalchemy.exc.DBAPIError:
            pass
            # logger.success("Таблицы для mail уже существуют в бд")
