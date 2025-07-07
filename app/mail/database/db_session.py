import sqlalchemy
from loguru import logger
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import CreateSchema
from starlette import status

from asyncdb import AsyncDB
from mail.database.models_mail import *

async_db_mail = AsyncDB()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session: Optional[AsyncSession] = None
    try:
        async with async_db_mail.AsyncSessionFactory() as session:
            logger.debug(f"Pool status: {async_db_mail.engine.pool.status()}")
            yield session
    except Exception as e:
        logger.error(f"Ошибка сессии: {e}")
        if session:
            await session.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="БД не доступна")

    finally:
        if session:
            await session.close()


async def create_tables_mail():
    async with async_db_mail.engine.begin() as conn:
        try:
            await conn.execute(CreateSchema('ospo'))
            # logger.success('Схема для ospo успешно создана!')
        except sqlalchemy.exc.ProgrammingError:
            # logger.success('Схема для mail уже сущесвует!')
            pass
            # logger.success("Схема для mail уже существует в БД")
        try:
            await conn.run_sync(Base.metadata.create_all)
            # await conn.run_sync(Base.metadata)
            # logger.success("Таблицы для mail успешно созданы")
        except sqlalchemy.exc.DBAPIError:
            # logger.success("Таблицы для mail уже существуют")
            pass
