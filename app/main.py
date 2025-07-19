import uvicorn
from loguru import logger
from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from mail.database.db_session import create_tables_mail
from mail.settings_mail_servers.settings_server import SettingsServer
from mail.api.api_mail import api_v1
from mail.api.api_websockets import api_ws
from mail.api.api_contacts import api_contacts
from mail.database.db_session import async_db_mail
from mail.schemas.tags_api import tags_metadata


# редис для авторизации в разработке
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.success('____________________________')
    logger.success('Запускается Почтовый сервер')

    redis_pool = None
    redis_client = None
    try:
        # Создаем пул соединений
        redis_pool = ConnectionPool(
            host=SettingsServer.REDIS_IP,
            port=SettingsServer.REDIS_PORT,
            password=SettingsServer.REDIS_PASS,
            max_connections=SettingsServer.REDIS_MAXCONN,  # Максимальное количество соединений
            socket_timeout=5,
            decode_responses=False,
            socket_connect_timeout=5,
            health_check_interval=30
        )

        # Проверяем подключение
        async with Redis(connection_pool=redis_pool) as redis_conn:
            await redis_conn.ping()

        redis_client = Redis(connection_pool=redis_pool)
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

        logger.success("Redis пул соединений инициализирован")
        app.state.redis_pool = redis_pool

        # Инициализация БД
        await async_db_mail.create_eng_session()
        logger.success("Подключение к БД установлено")

        yield

    except Exception as e:
        logger.error(f"Ошибка инициализации: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось инициализировать сервисы ошибка: {e}"
        )
    finally:
        if redis_pool:
            await redis_pool.disconnect()
            logger.success("Redis пул соединений закрыт")
        logger.success("Работа Почтового сервера завершена!")


app = FastAPI(
    title="Почта Rubin",
    description="API для работы с почтовой системой Rubin",
    debug=True,
    version="0.1",
    lifespan=lifespan,
    # dependencies=[Depends()],
    openapi_tags=tags_metadata)

# static_dir_handbook = os.path.join(os.path.dirname(__file__), "mail/static")
# app.mount("/mail/static", StaticFiles(directory=static_dir_handbook, html=True),
#           name="/mail/static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Только для ASTRA linux Мандатных атрибутов
@app.middleware("http")
async def add_basic_auth_header(request, call_next):
    response = await call_next(request)
    if response.status_code == 401 and "www-authenticate" not in response.headers:
        response.headers["WWW-Authenticate"] = 'Basic realm="Secure Area"'
        response.headers["Connection"] = "keep-alive"
    response.headers["Connection"] = "keep-alive"
    if "authorization" in request.headers:
        response.headers["authorization"] = request.headers["authorization"]
    return response


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


app.include_router(api_v1)
app.include_router(api_ws)
app.include_router(api_contacts)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
