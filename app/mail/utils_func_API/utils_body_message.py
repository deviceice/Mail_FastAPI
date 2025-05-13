from mail.utils_func_API.utils_func import *
from email import policy
from email.parser import BytesParser
import base64
import quopri
import re


async def get_email_body_test(response):
    """
    Получает тело письма по UID и декодирует его.
    """
    # Извлекаем тело письма
    raw_email = response  # BODY[1] содержит тело письма
    if isinstance(raw_email, bytearray):
        raw_email = raw_email.decode("utf-8", errors="ignore")

    # Парсим письмо
    msg = BytesParser(policy=policy.default).parsebytes(raw_email.encode("utf-8"))

    # Получаем кодировку из заголовка
    content_type = msg.get("Content-Type", "")
    charset = "utf-8"  # По умолчанию
    if "charset=" in content_type:
        charset = content_type.split("charset=")[1].split(";")[0].strip('"')

    # Получаем тело письма
    body = msg.get_payload(decode=True)

    # Декодируем тело письма
    if msg.get("Content-Transfer-Encoding") == "base64":
        body = base64.b64decode(body)
    elif msg.get("Content-Transfer-Encoding") == "quoted-printable":
        body = quopri.decodestring(body)
    else:
        body = body  # Если кодировка не указана, оставляем как есть

    # Декодируем в строку с учетом кодировки
    try:
        body = body.decode(charset)
    except UnicodeDecodeError:
        # Если не удалось декодировать, пробуем другие кодировки
        try:
            body = body.decode("cp1251")  # Попробуем Windows-1251
        except UnicodeDecodeError:
            body = body.decode("iso-8859-1")  # Попробуем ISO-8859-1

    return body


async def get_name_attachments(bodystructure):
    """
    Парсит bodystructure и взращает list в котором dicts [{"filename": text.txt, "size":213},]
    """
    attachment_pattern = re.compile(
        rb'\(["\']?attachment["\']?\s+\(["\']?filename["\']?\s+["\']([^"\']+)["\']\s+["\']?size["\']?\s+["\']?(\d+)["\']?\)')

    bodystructure_search = attachment_pattern.findall(bodystructure)
    parsed_attachments = []
    if bodystructure_search:
        parsed_attachments = [
            {"filename": filename.decode(), "size": await format_size(int(size.decode()))}
            for filename, size in bodystructure_search
        ]
    return parsed_attachments
