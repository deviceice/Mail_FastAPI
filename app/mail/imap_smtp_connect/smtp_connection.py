import asyncio
import time

import aiosmtplib
from typing import Union
from contextlib import asynccontextmanager
from fastapi import HTTPException
from starlette import status as status_code
from collections import defaultdict
from loguru import logger

from mail.http_exceptions.default_exception import HTTPExceptionMail
from mail.settings_mail_servers.settings_server import SettingsServer
from mail.imap_smtp_connect.timed_connection import TimedConnection


class SMTPPool:
    def __init__(self, expiry_seconds: int = 1800,  # 30 минут по умолчанию
                 timeout: Union[int, float] = 1.5):
        self.pools = defaultdict(asyncio.Queue)
        self.expiry_seconds = expiry_seconds  # Время жизни соединения в секундах
        self.timeout_connect = timeout  # Таймаут на подключение к IMAP серверу

    @asynccontextmanager
    async def get_connection(self, user: str, password: str):
        pool = self.pools[user]
        timed_conn = None
        smtp = None
        try:
            if pool.empty():
                smtp = await self._create_smtp_connection(user, password)
                timed_conn = TimedConnection(smtp)
            else:
                timed_conn = await pool.get()
                if timed_conn.is_expired(self.expiry_seconds) or not timed_conn.connection.is_connected:
                    logger.warning("Соединение устарело или неактивно. Пересоздаем...")
                    # await self._close_connection(timed_conn.connection)
                    smtp = await self._create_smtp_connection(user, password)
                    timed_conn = TimedConnection(smtp)
                    await pool.put(timed_conn)
                else:
                    smtp = timed_conn.connection
                if not smtp.is_connected:
                    raise HTTPExceptionMail.SMTP_TIMEOUT_504

            yield smtp
        finally:
            if smtp:
                try:
                    if smtp.is_connected:
                        timed_conn.last_used = time.time()
                        await pool.put(timed_conn)
                    else:
                        logger.warning("Соединение неактивно, не возвращаем в пул")
                        await self._close_smtp_connection(smtp)
                except Exception as e:
                    logger.error(f"Ошибка при возврате соединения: {e}")

    async def _create_smtp_connection(self, user: str, password: str):
        smtp = aiosmtplib.SMTP(hostname=SettingsServer.SMTP_HOST,
                               port=SettingsServer.SMTP_PORT,
                               timeout=self.timeout_connect)
        try:
            await smtp.connect()
            if not smtp.is_connected:
                raise HTTPExceptionMail.SMTP_TIMEOUT_504

            status, response = await smtp.login(user, password)
            if response not in ('Authentication succeeded'):
                raise HTTPExceptionMail.NOT_AUTHENTICATED_401
            else:
                return smtp
        except Exception as e:
            logger.error(f"Ошибка при создании SMTP соединения: {e}")
            raise HTTPExceptionMail.SMTP_TIMEOUT_504

    async def _close_smtp_connection(self, smtp):
        try:
            await smtp.close()
        except Exception as e:
            logger.error(f"Ошибка при закрытии: {e}")



smtp_pool = SMTPPool(expiry_seconds=1800)


async def get_smtp_connection():
    user = 'user'  # test
    password = '12345678'  # test
    async with smtp_pool.get_connection(user, password) as smtp:
        yield smtp
