import os
import urllib.parse
import uuid

import aiofiles
import mimetypes

from datetime import datetime, timezone, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path

from mail.schemas.request.schemas_mail_req import EmailSend
from mail.options_emails import EmailFlags
from mail.settings_mail_servers.settings_server import SettingsServer

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
    message["Message-ID"] = str(uuid.uuid4()) + '@' + SettingsServer.SMTP_HOST
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
        return FileNotFoundError(f"File {attachment.filename} not found.")

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
    return part

# TEST CELERY

# def create_email_with_attachments(email: EmailSend, from_user):
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
#             part = process_attachment(attachment)
#             message.attach(part)
#
#     return message
#
#
# def process_attachment(attachment):
#     file_path = UPLOAD_DIR / attachment.uuid
#     # Асинхронная проверка файла
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"File {attachment.filename} not found.")
#
#     mime_type, _ = mimetypes.guess_type(attachment.filename)
#     mime_type = mime_type or 'application/octet-stream'
#     maintype, subtype = mime_type.split('/', 1)
#
#     # Выносим CPU-bound операции в отдельный поток
#
#     # Чтение файла асинхронно
#     with open(file_path, 'rb') as f:
#         file_data = f.read()
#
#     part = MIMEBase(maintype, subtype)
#     part.set_payload(file_data)
#     encoders.encode_base64(part)
#     filename_encoded = urllib.parse.quote(attachment.filename, safe='', encoding='utf-8')
#     part.add_header(
#         "Content-Disposition",
#         f'attachment; filename="{filename_encoded}"; filename*={filename_encoded}; size={len(file_data)}'
#     )
#     return part
