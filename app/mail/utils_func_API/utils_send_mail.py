import asyncio
import base64
import io
import os
import tempfile
import urllib.parse
from datetime import datetime, timezone, timedelta
from email import encoders
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from typing import List
from loguru import logger

import aiofiles

from mail.schemas.request.schemas_mail_req import EmailSend
from mail.options_emails import EmailFlags
import mimetypes

BASE_DIR_APP = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR_APP / 'temp'


async def append_inbox_message_in_sent(message, imap):
    """
    Копирует сообщение в папку Отправленные с Флагом прочитано
    """
    await imap.append(message_bytes=message.as_bytes(), mailbox='Sent', flags=EmailFlags.flags['seen'])


async def append_inbox_message_in_drafts(message, imap):
    """
    Копирует сообщение в папку Отправленные с Флагом прочитано
    """
    await imap.append(message_bytes=message.as_bytes(), mailbox='Drafts', flags=EmailFlags.flags['seen'])


# async def create_email_with_attachments(email: EmailSend, from_user):
#     """
#     Создает MIME-сообщение с вложениями, если они есть, или без них.
#     """
#     has_attachments = bool(email.attachments)
#
#     if has_attachments:
#         message = MIMEMultipart()
#         message.attach(MIMEText(email.body, "plain"))
#     else:
#         message = MIMEText(email.body, "plain")
#
#     date = formatdate(datetime.now(timezone(timedelta(hours=3))).timestamp(), localtime=True)
#     message["From"] = from_user
#     message["To"] = email.to if isinstance(email.to, str) else ", ".join(email.to)
#     message["Subject"] = f'{email.subject}' if email.subject else ''
#     message["Date"] = date
#     if email.reference:
#         message["References"] = f'<{email.reference}>'
#
#     if has_attachments:
#         for attachment in email.attachments:
#             mime_type, _ = mimetypes.guess_type(attachment.filename)
#             mime_type = mime_type or 'application/octet-stream'
#             main_type, sub_type = mime_type.split('/', 1)
#             part = MIMEBase(main_type, sub_type)
#
#             decoded_data = base64.b64decode(attachment.file)
#             part.set_payload(decoded_data)
#             encoders.encode_base64(part)
#
#             filename_encoded = urllib.parse.quote(attachment.filename, safe='', encoding='utf-8')
#             part.add_header(
#                 "Content-Disposition",
#                 f'attachment; filename="{filename_encoded}"; filename*={filename_encoded}; size={len(decoded_data)}'
#             )
#             message.attach(part)
#
#     return message


# 2
async def create_email_with_attachments(email: EmailSend, from_user):
    """
    Создает MIME-сообщение с вложениями, если они есть, или без них.
    """
    has_attachments = bool(email.attachments)

    if has_attachments:
        message = MIMEMultipart()
        message.attach(MIMEText(email.body, "plain"))
    else:
        message = MIMEText(email.body, "plain")

    date = formatdate(datetime.now(timezone(timedelta(hours=3))).timestamp(), localtime=True)
    message["From"] = from_user
    message["To"] = email.to if isinstance(email.to, str) else ", ".join(email.to)
    message["Subject"] = f'{email.subject}' if email.subject else ''
    message["Date"] = date
    if email.reference:
        message["References"] = f'<{email.reference}>'

    if has_attachments:
        for attachment in email.attachments:
            part = await process_attachment(attachment)
            message.attach(part)

    return message


async def process_attachment(attachment):
    file_path = UPLOAD_DIR / attachment.uuid
    # Асинхронная проверка файла
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {attachment.filename} not found.")

    mime_type, _ = mimetypes.guess_type(attachment.filename)
    mime_type = mime_type or 'application/octet-stream'
    maintype, subtype = mime_type.split('/', 1)

    # Выносим CPU-bound операции в отдельный поток

    # Чтение файла асинхронно
    async with aiofiles.open(file_path, 'rb') as f:
        file_data = await f.read()

    part = MIMEBase(maintype, subtype)
    part.set_payload(file_data)
    encoders.encode_base64(part)
    filename_encoded = urllib.parse.quote(attachment.filename, safe='', encoding='utf-8')
    part.add_header(
        "Content-Disposition",
        f'attachment; filename="{filename_encoded}"; filename*={filename_encoded}; size={len(file_data)}'
    )

    # mime_type, _ = mimetypes.guess_type(attachment.filename)
    # mime_type = mime_type or 'application/octet-stream'
    # main_type, sub_type = mime_type.split('/', 1)
    # part = MIMEBase(main_type, sub_type)
    # decoded_data = base64.b64decode(attachment.file)
    # part.set_payload(decoded_data)
    # encoders.encode_base64(part)
    # filename_encoded = urllib.parse.quote(attachment.filename, safe='', encoding='utf-8')
    # part.add_header(
    #     "Content-Disposition",
    #     f'attachment; filename="{filename_encoded}"; filename*={filename_encoded}; size={len(decoded_data)}'
    # )
    return part

# async def create_email_with_attachments(email: EmailSend, from_user: str):
#     msg = EmailMessage()
#     msg["From"] = from_user
#     msg["To"] = email.to if isinstance(email.to, str) else ", ".join(email.to)
#     msg["Subject"] = email.subject or ''
#     msg["Date"] = formatdate(datetime.now(timezone(timedelta(hours=3))).timestamp(), localtime=True)
#     if email.reference:
#         msg["References"] = f'<{email.reference}>'
#
#     msg.set_content(email.body)
#
#     # Добавляем вложения
#     attach_tasks = [
#         attach_file_streaming(msg, attachment)
#         for attachment in email.attachments
#     ]
#     await asyncio.gather(*attach_tasks)
#     return msg
#
#
# async def attach_file_streaming(msg: EmailMessage, attachment):
#     file_path = UPLOAD_DIR / attachment.uuid
#
#     # Асинхронная проверка файла
#     if not await aiofiles.os.path.exists(file_path):
#         raise FileNotFoundError(f"File {attachment.filename} not found.")
#
#     mime_type, _ = mimetypes.guess_type(attachment.filename)
#     mime_type = mime_type or 'application/octet-stream'
#     maintype, subtype = mime_type.split('/', 1)
#
#     # Выносим CPU-bound операции в отдельный поток
#
#     filename_encoded = urllib.parse.quote(attachment.filename, safe='', encoding='utf-8')
#
#     # Чтение файла асинхронно
#     async with aiofiles.open(file_path, 'rb') as f:
#         file_data = await f.read()
#
#     # Выносим добавление вложения в отдельный поток
#     def _sync_add_attachment():
#         msg.add_attachment(
#             file_data,
#             maintype=maintype,
#             subtype=subtype,
#             filename=filename_encoded,
#         )
#
#     await asyncio.to_thread(_sync_add_attachment)
