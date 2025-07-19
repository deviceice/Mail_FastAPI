from fastapi import HTTPException
from starlette import status as status_code


class HTTPExceptionMail:
    IMAP_TIMEOUT_504 = HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                                     detail='Сервер IMAP не ответил')

    SMTP_TIMEOUT_504 = HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                                     detail='Сервер SMTP не ответил')

    SMTP_TOO_MANY_REQUESTS_429 = HTTPException(status_code=status_code.HTTP_429_TOO_MANY_REQUESTS,
                                               detail='Превышено колличество запросов к SMTP серверу')

    IMAP_TOO_MANY_REQUESTS_429 = HTTPException(status_code=status_code.HTTP_429_TOO_MANY_REQUESTS,
                                               detail='Превышено колличество запросов к IMAP серверу')

    FOLDER_NOT_FOUND_404 = HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                                         detail="Папка не найдена в почтовом ящике")

    MESSAGE_NOT_FOUND_404 = HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                                          detail=f"Письмо не найдено с таким UID")

    FILE_NOT_FOUND_404 = HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                                       detail=f"Файл не найден с таким номером")

    ERROR_CODING_FOLDER_400 = HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST,
                                            detail=f"Ошибка кодирования имени папки")

    MOVING_COPY_MESSAGE_ERROR_409 = HTTPException(status_code=status_code.HTTP_409_CONFLICT,
                                                  detail=f"Не удалось переместить письмо")
    ERROR_IN_BACKEND_SERVER_500 = HTTPException(status_code=status_code.HTTP_503_SERVICE_UNAVAILABLE,
                                                detail=f"Ошибка в Backend, сообщите разработчику для исправления")

    NOT_AUTHENTICATED_401 = HTTPException(status_code=status_code.HTTP_401_UNAUTHORIZED,
                                          detail='Не правильный логин или пароль')

    ERROR_DELETES_MAILS_304 = HTTPException(status_code=status_code.HTTP_304_NOT_MODIFIED,
                                            detail='Не удалось удалить сообщения')

    ERROR_SAVED_FILE_400 = HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST,
                                            detail='Не удалось загрузить файлы')
    NOT_CONNECTED_DB_503 = HTTPException(status_code=status_code.HTTP_503_SERVICE_UNAVAILABLE,
                                         detail='База данных недоступна')

