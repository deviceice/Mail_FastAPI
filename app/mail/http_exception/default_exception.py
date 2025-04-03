from fastapi import HTTPException
from starlette import status as status_code


class HttpExceptionMail:
    IMAP_TIMEOUT_504 = HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                                     detail='Сервер IMAP не ответил')

    SMTP_TOO_MANY_REQUESTS_429 = HTTPException(status_code=status_code.HTTP_429_TOO_MANY_REQUESTS,
                                               detail='Превышено колличество запросов к SMTP серверу')

    IMAP_TOO_MANY_REQUESTS_429 = HTTPException(status_code=status_code.HTTP_429_TOO_MANY_REQUESTS,
                                               detail='Превышено колличество запросов к IMAP серверу')

    FOLDER_NOT_FOUND_404 = HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                                         detail="Папка не найдена в почтовом ящике")

    MESSAGE_NOT_FOUND_404 = HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                                          detail=f"Письмо не найдено с таким UID")

    ERROR_CODING_FOLDER_400 = HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST,
                                            detail=f"Ошибка кодирования имени папки")

    MOVING_COPY_MESSAGE_ERROR_409 = HTTPException(status_code=status_code.HTTP_409_CONFLICT,
                                                  detail=f"Не удалось переместить письмо")
    ERORR_IN_BACKEND_SERVER_500 = HTTPException(status_code=status_code.HTTP_503_SERVICE_UNAVAILABLE,
                                                detail=f"Ошибка в Backend, сообщине разработчику для исправления")

    NOT_AUTHENTICATED_401 = HTTPException(status_code=401, detail='Не правильный логин или пароль')
