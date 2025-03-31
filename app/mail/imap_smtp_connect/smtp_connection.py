import asyncio
import aiosmtplib
from mail.setting_mail_server.settings_server import SettingsServer
from contextlib import asynccontextmanager
from fastapi import HTTPException
from starlette import status as status_code
from collections import defaultdict
from loguru import logger


class SMTPPool:
    def __init__(self):
        self.pools = defaultdict(asyncio.Queue)

    @asynccontextmanager
    async def get_connection(self, user: str, password: str):
        pool = self.pools[user]
        if pool.empty():
            smtp = await self._create_smtp_connection(user, password)
        else:
            smtp = await pool.get()
        try:
            if not smtp.is_connected:
                try:
                    await smtp.quit()
                except Exception:
                    pass
                smtp = await self._create_smtp_connection(user, password)
            yield smtp
        finally:
            await pool.put(smtp)

    async def _create_smtp_connection(self, user: str, password: str):
        smtp = aiosmtplib.SMTP()
        try:
            await smtp.connect(hostname=SettingsServer.SMTP_IP, port=SettingsServer.SMTP_PORT)
            if not smtp.is_connected:
                raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                                    detail='Сервер SMTP не отвечает')

            status, response = await smtp.login(user, password)
            if response not in ('Authentication succeeded'):
                raise HTTPException(status_code=status_code.HTTP_401_UNAUTHORIZED,
                                    detail='Не правильный логин или пароль')
            else:
                return smtp
        except Exception as e:
            logger.error(f"Ошибка при создании SMTP соединения: {e}")
            raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                                detail='Сервер SMTP не отвечает')


smtp_pool = SMTPPool()


async def get_smtp_connection():
    user = 'user'  # test
    password = '12345678'  # test
    async with smtp_pool.get_connection(user, password) as smtp:
        yield smtp

# smtp_pools = defaultdict(asyncio.Queue)
#
# @asynccontextmanager
# async def smtp_connection_pool(user, password):
#     pool = smtp_pools[user]
#     if pool.empty():
#         smtp = await create_smtp_connection(user, password)
#     else:
#         smtp = await pool.get()
#     try:
#         if not smtp.is_connected:
#             try:
#                 await smtp.quit()
#             except Exception:
#                 pass
#             smtp = await create_smtp_connection(user, password)
#         yield smtp
#     finally:
#         await pool.put(smtp)
#
#
# async def create_smtp_connection(user, password):
#     smtp = aiosmtplib.SMTP()
#     try:
#         await smtp.connect(hostname=SettingsServer.SMTP_IP, port=SettingsServer.SMTP_PORT)
#         if not smtp.is_connected:
#             return {'status': False, 'message': 'SMTP сервер не отвечает'}
#
#         status, response = await smtp.login(user, password)
#         if response not in ('Authentication succeeded'):
#             return {'status': False, 'message': response}
#         else:
#             return smtp
#     except Exception as e:
#         logger.error(f"Ошибка при создании SMTP соединения: {e}")
#         return {'status': False, 'message': 'Ошибка при создании SMTP соединения'}
