import asyncio
import aioimaplib
from fastapi import HTTPException
from starlette import status as status_code

from mail.setting_mail_server.settings_server import SettingsServer
from mail.http_exception.default_exception import HttpExceptionMail as HttpMailError
from contextlib import asynccontextmanager
from collections import defaultdict
from loguru import logger


# class IMAPPool:
#     def __init__(self):
#         self.pools = defaultdict(asyncio.Queue)
#
#     @asynccontextmanager
#     async def get_connection(self, user: str, password: str):
#         pool = self.pools[user]
#         if pool.empty():
#             imap = await self._create_imap_connection(user, password)
#         else:
#             imap = await pool.get()
#
#         try:
#             if not await self._is_connection_active(imap):
#                 logger.warning("Соединение неактивно. Пересоздаем...")
#                 imap = await self._create_imap_connection(user, password)
#
#
#             yield imap
#         finally:
#             try:
#                 await pool.put(imap)
#             except Exception as e:
#                 logger.error(f"Ошибка при возвращении соединения в пул и закрытия папки в почтовом ящике: {e}")
#                 await self._close_connection(imap)
#
#     async def _create_imap_connection(self, user: str, password: str):
#         imap = aioimaplib.IMAP4(host=SettingsServer.IMAP_IP, port=SettingsServer.IMAP_PORT, timeout=1.5)
#         try:
#             await imap.wait_hello_from_server()
#         except Exception as e:
#             raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
#                             detail=f'Сервер IMAP не ответил : {e}')
#         status, response = await imap.login(user, password)
#         if status == 'NO':
#             raise HTTPException(status_code=status_code.HTTP_401_UNAUTHORIZED, detail='Не правильный логин или пароль')
#         if status != 'OK':
#             raise HTTPException(status_code=status_code.HTTP_429_TOO_MANY_REQUESTS, detail='Превышено количество запросов к IMAP серверу')
#         return imap
#
#     async def _is_connection_active(self, imap):
#         try:
#             status, response = await imap.noop()
#             return status == 'OK' and imap.get_state() not in ('LOGOUT', 'NON_AUTH')
#         except (asyncio.TimeoutError, aioimaplib.Abort, Exception) as e:
#             logger.error(f'Ошибка при проверке соединения - {e}')
#             return False
#
#     async def close_all_connections(self):
#         for user, pool in self.pools.items():
#             while not pool.empty():
#                 imap = await pool.get()
#                 await self._close_connection(imap)
#
#     async def _close_connection(self, imap):
#         try:
#             await imap.close()
#             await imap.logout()
#             await imap.quit()
#         except Exception as e:
#             logger.error(f"Ошибка при закрытии соединения: {e}")
#         finally:
#             if hasattr(imap, 'close'):
#                 await imap.close()


class IMAPPool:
    def __init__(self):
        self.pools = defaultdict(asyncio.Queue)

    @asynccontextmanager
    async def get_connection(self, user: str, password: str):
        pool = self.pools[user]
        imap = None
        if pool.empty():
            imap = await self._create_imap_connection(user, password)
        else:
            imap = await pool.get()
            if not await self._is_connection_active(imap):
                logger.warning("Соединение неактивно. Пересоздаем...")
                await self._close_connection(imap)
                imap = await self._create_imap_connection(user, password)
        try:
            if not await self._is_connection_active(imap):
                raise HttpMailError.IMAP_TIMEOUT_504
            yield imap
        finally:
            if imap:
                try:
                    # Проверяем активность перед возвратом в пул
                    if await self._is_connection_active(imap):
                        await pool.put(imap)
                    else:
                        logger.warning("Соединение неактивно, не возвращаем в пул")
                        await self._close_connection(imap)
                except Exception as e:
                    logger.error(f"Ошибка при возврате соединения: {e}")
                    await self._close_connection(imap)

    async def _create_imap_connection(self, user: str, password: str):
        imap = aioimaplib.IMAP4(host=SettingsServer.IMAP_IP, port=SettingsServer.IMAP_PORT, timeout=1.5)
        try:
            await imap.wait_hello_from_server()
        except Exception as e:
            raise HttpMailError.IMAP_TIMEOUT_504
        status, response = await imap.login(user, password)
        if status == 'NO':
            raise HttpMailError.NOT_AUTHENTICATED_401
        if status != 'OK':
            raise HttpMailError.IMAP_TOO_MANY_REQUESTS_429
        return imap

    async def _is_connection_active(self, imap):
        try:
            status, response = await imap.noop()
            return status == 'OK' and imap.get_state() not in ('LOGOUT', 'NON_AUTH')
        except (asyncio.TimeoutError, aioimaplib.Abort, Exception) as e:
            logger.error(f'Не смог приконнектиться: {e}')
            return False

    async def close_all_connections(self):
        for user, pool in self.pools.items():
            while not pool.empty():
                imap = await pool.get()
                await self._close_connection(imap)

    async def _close_connection(self, imap):
        try:
            await imap.close()
        except Exception:
            pass
        try:
            await imap.logout()
        except Exception:
            pass
        # try:
        #     await imap.quit()
        # except Exception:
        #     pass




imap_pool = IMAPPool()


async def get_imap_connection():
    user = 'user'  # test
    password = '12345678'  # test
    async with imap_pool.get_connection(user, password) as imap:
        yield imap
