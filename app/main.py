import uvicorn
from loguru import logger
from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from mail.database.db_session import create_tables_mail
from mail.api.api_mail import api_v1
from mail.api.api_websockets import api_ws
from mail.api.api_contacts import api_contacts
from mail.database.db_session import async_db_mail
from mail.schemas.tags_api import tags_metadata


#редис для авторизации в разработке
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.success('____________________________')
    logger.success('Запускается Почтовый сервер')

    redis_pool = None
    try:
        # Создаем пул соединений
        # redis_pool = ConnectionPool(
        #     host="20.0.0.123",
        #     port=6379,
        #     password='12345678',
        #     max_connections=20,  # Максимальное количество соединений
        #     decode_responses=True,
        #     socket_timeout=5,
        #     socket_connect_timeout=5,
        #     health_check_interval=30
        # )
        #
        # # Проверяем подключение
        # async with Redis(connection_pool=redis_pool) as redis_conn:
        #     await redis_conn.ping()
        #
        # logger.success("Redis пул соединений инициализирован")
        # app.state.redis_pool = redis_pool

        # Инициализация БД
        await async_db_mail.create_eng_session('DB_MAIL')
        logger.success("Подключение к БД установлено")

        yield

    except Exception as e:
        logger.error(f"Ошибка инициализации: {e}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось инициализировать сервисы"
        )
    finally:
        # if redis_pool:
        #     await redis_pool.disconnect()
        #     logger.success("Redis пул соединений закрыт")
        logger.success("Работа Почтового сервера завершена!")


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.success('____________________________')
#     logger.success('Запускается Почтовый сервер')
#
#     # Инициализация Redis
#     redis_conn = None
#     try:
#         # Подключение к Redis
#         redis_conn = Redis.Redis(
#             host="20.0.0.130",
#             port=6379,
#             password='12345678',
#             decode_responses=True,
#             socket_timeout=5,
#             socket_connect_timeout=5,
#             health_check_interval=30  # проверка соединения каждые 30 секунд
#         )
#
#         # Проверка подключения
#         await redis_conn.ping()
#         logger.success("Подключение к Redis установлено")
#         app.state.redis = redis_conn
#
#         # Инициализация БД
#         await async_db_mail.create_eng_session('DB_MAIL')
#         logger.success("Подключение к БД установлено")
#
#         yield
#
#     except Exception as e:
#         logger.error(f"Ошибка инициализации: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="Не удалось инициализировать сервисы"
#         )
#     finally:
#         if redis_conn:
#             await redis_conn.close()
#             logger.success("Подключение к Redis закрыто")
#         logger.success("Работа Почтового сервера завершена!")

app = FastAPI(title="Почта Rubin",
              debug=True,
              version="0.1",
              lifespan=lifespan,
              # dependencies= [Аутентификация по JWT],
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


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


app.include_router(api_v1)
app.include_router(api_ws)
app.include_router(api_contacts)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
