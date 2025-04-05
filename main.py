import uvicorn
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mail.database.db_session import create_tables_mail
from mail.api_mail import api_v1
from loguru import logger
from mail.database.db_session import async_db_mail
from mail.imap_smtp_connect.imap_connection import IMAPPool
from mail.schemas.tags_api import tags_metadata


# редис для авторизации в разработке
async def lifespan(_app: FastAPI):
    logger.success('_______________________________________________________________________________________________')
    logger.success('Запускается Почтовый сервер')
    # redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    # _app.state.redis = redis
    try:
        await async_db_mail.create_eng_session('DB_MAIL')
        await create_tables_mail()
        # await redis.ping()
        # logger.success("Подключение к Redis установлено")
        # _app.state.celery = create_celery_app()
        yield
    except Exception as e:
        logger.error(f"Не удалось подключиться к бд чтобы создать таблицы   {e}")
        yield
    finally:
        logger.success("Работа Почтового сервера завершена!")
        # await redis.close()
        # logger.success("Подключение к Redis закрыто")


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
async def custom_http_exception_handler(exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


app.include_router(api_v1)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
