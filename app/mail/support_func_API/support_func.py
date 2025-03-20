import base64
import binascii
import re

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

from email.header import decode_header
from mail.schemas.request_schemas import *


async def format_size(size_bytes):
    # Преобразуем размер в читаемый формат
    if size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024 * 1024:
        return f"{round(size_bytes / 1024, 2)} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{round(size_bytes / (1024 * 1024), 2)} MB"
    else:
        return f"{round(size_bytes / (1024 * 1024 * 1024), 2)} GB"


async def parse_folders(response):
    # Возвращает все папки пользователя уже раскодированными
    folders = []
    for line in response:
        if not line.startswith(b'('):
            continue
        line_str = line.decode()
        parts = line_str.split()
        folder_name = parts[-1]
        if folder_name.startswith('"') and folder_name.endswith('"'):
            folder_name = folder_name[1:-1]
        folder_name = await decode_name_ascii_utf7(folder_name)
        folders.append(folder_name)
    return folders


async def get_decode_header_subject(message):
    # Возвращает декодированный Subject из Header
    if message["Subject"] is None:
        return ''
    encoding = decode_header(message["Subject"])[0][1]
    if encoding is None:
        return decode_header(message["Subject"])[0][0]
    else:
        return decode_header(message["Subject"])[0][0].decode(encoding)


async def decode_name_ascii_utf7(name: str) -> str:
    return name.encode('ascii').decode('utf-7')


async def encode_name_utf7_ascii(name: str) -> str:
    return name.encode('utf-7').decode('ascii')


async def get_attachments(message):
    # Получает из сообщения все attachemnts и возвращает список диктов
    attachments = []
    if message.is_multipart():
        for part in message.walk():
            content_disposition = part.get("Content-Disposition", "")
            if "attachment" in content_disposition or "filename" in content_disposition:
                filename = part.get_filename()
                if filename:
                    file_data = part.get_payload(decode=True)
                    attachments.append({
                        "filename": filename,
                        "content_type": part.get_content_type(),
                        "size": await format_size(len(file_data)),
                        "data": base64.b64encode(file_data).decode()
                    })
    return attachments
