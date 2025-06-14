import asyncio
import json

from fastapi import Request, HTTPException, status, WebSocket
from mail.imap_lib.aioimaplib import aioimaplib
import time
from typing import Union
from contextlib import asynccontextmanager
from collections import defaultdict
from loguru import logger
from mail.settings_mail_servers.settings_server import SettingsServer
from mail.http_exceptions.default_exception import HTTPExceptionMail
from mail.imap_smtp_connect.timed_connection import TimedConnection
import ctypes
import socket
import base64


# redis: Redis = Depends(lambda: app.state.redis) redis подключение редис
# Пулы соединений хранятся только локально, при масштабировании нужна привязка в Nginx к  инстансу


class IMAPPool:
    def __init__(self, expiry_seconds: int = 1800,  # 30 минут по умолчанию
                 timeout: Union[int, float] = 30):
        self.pools = defaultdict(asyncio.Queue)
        self.expiry_seconds = expiry_seconds  # Время жизни соединения в секундах
        self.timeout_connect = timeout  # Таймаут на подключение к IMAP серверу

    @asynccontextmanager
    async def get_connection(self, user: str, password: str):
        pool = self.pools[user]
        timed_conn = None
        imap = None

        try:
            if pool.empty():
                imap = await self._create_imap_connection(user, password)
                timed_conn = TimedConnection(imap)
            else:
                timed_conn = await pool.get()
                if timed_conn.is_expired(self.expiry_seconds) or not await self._is_connection_active(
                        timed_conn.connection):
                    logger.warning("Соединение устарело или неактивно. Пересоздаем...")
                    imap = await self._create_imap_connection(user, password)
                    timed_conn = TimedConnection(imap)
                else:
                    imap = timed_conn.connection

            if not await self._is_connection_active(imap):
                raise HTTPExceptionMail.IMAP_TIMEOUT_504
            # imap = await self._create_imap_connection(user, password)
            # if not await self._is_connection_active(imap):
            #     raise HTTPExceptionMail.IMAP_TIMEOUT_504
            yield imap

        finally:
            if imap:
                try:
                    if imap.get_state() in 'AUTH':
                        print(imap.get_state())
                        pass
                        # await imap.logout()
                    else:
                        await imap.close()
                        # await imap.logout()
                    if await self._is_connection_active(imap):
                        timed_conn.last_used = time.time()
                        await pool.put(timed_conn)
                    else:
                        logger.warning("Соединение неактивно, не возвращаем в пул")
                        await self._close_connection(imap)
                except Exception as e:
                    logger.error(f"Ошибка при возврате соединения: {e}")
                    await self._close_connection(imap)

    async def _create_imap_connection(self, user: str, password: str):
        imap = aioimaplib.IMAP4(
            host=SettingsServer.IMAP_HOST,
            port=SettingsServer.IMAP_PORT,
            timeout=self.timeout_connect
        )
        try:
            status = await imap.wait_hello_from_server()
            print(status)
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            raise HTTPExceptionMail.IMAP_TIMEOUT_504
        try:
            status, response = await imap.login(user, password)
        except asyncio.exceptions.TimeoutError:
            raise HTTPExceptionMail.IMAP_TIMEOUT_504
        if status == 'NO':
            print(status, response)
            raise HTTPExceptionMail.NOT_AUTHENTICATED_401
        if status != 'OK':
            raise HTTPExceptionMail.IMAP_TOO_MANY_REQUESTS_429
        return imap

    async def _is_connection_active(self, imap) -> bool:
        try:
            status, _ = await imap.noop(timeout=0.2)
            return status == 'OK' and imap.get_state() not in ('LOGOUT', 'NON_AUTH')
        except (asyncio.TimeoutError, aioimaplib.Abort, Exception) as e:
            logger.error(f"Ошибка проверки активности: {e}")
            return False

    async def close_all_connections(self):
        for user, pool in self.pools.items():
            while not pool.empty():
                timed_conn = await pool.get()
                await self._close_connection(timed_conn.connection)

    async def _close_connection(self, imap):
        try:
            await imap.close()
        except Exception as e:
            pass
            logger.error(f"Ошибка при закрытии: {e}")
        try:
            await imap.logout()
        except Exception as e:
            logger.error(f"Ошибка при выходе: {e}")


imap_pool = IMAPPool(expiry_seconds=1800)


async def get_imap_connection(request: Request):
    auth_header = request.headers.get("authorization")
    # Временное решение пока не поднял REDIS
    encoded_credentials = auth_header.split(" ")[1]
    decoded_bytes = base64.b64decode(encoded_credentials)
    decoded_credentials = decoded_bytes.decode("utf-8")
    try:
        username, password = decoded_credentials.split(":", 1)
    except ValueError:
        raise HTTPExceptionMail.NOT_AUTHENTICATED_401
    async with imap_pool.get_connection(username, password) as imap:
        yield imap


async def get_imap_connection_ws(websocket: WebSocket):
    await websocket.accept()
    message = await websocket.receive_text()
    data = json.loads(message)
    if not data['Authorization']:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        token = data.get('Authorization')
        if token and token.startswith("Basic "):
            token = token[6:]
        decoded_bytes = base64.b64decode(token)
        decoded_credentials = decoded_bytes.decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
    except Exception:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return
    async with imap_pool.get_connection(username, password) as imap:
        yield imap
