import base64
import urllib.parse
from datetime import datetime, timezone, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from mail.schemas.request.schemas_mail_req import EmailSend
import mimetypes


async def append_inbox_message_in_sent(message, imap):
    """
    Копирует сообщение в папку Отправленные с Флагом прочитано
    """
    await imap.append(message_bytes=message.as_bytes(), mailbox='Sent', flags='\\Seen', )


async def append_inbox_message_in_drafts(message, imap):
    """
    Копирует сообщение в папку Отправленные с Флагом прочитано
    """
    await imap.append(message_bytes=message.as_bytes(), mailbox='Drafts', flags='\\Seen', )


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
            mime_type, _ = mimetypes.guess_type(attachment.filename)
            mime_type = mime_type or 'application/octet-stream'
            main_type, sub_type = mime_type.split('/', 1)
            part = MIMEBase(main_type, sub_type)

            decoded_data = base64.b64decode(attachment.file)
            part.set_payload(decoded_data)
            encoders.encode_base64(part)

            filename_encoded = urllib.parse.quote(attachment.filename, safe='', encoding='utf-8')
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{filename_encoded}"; filename*={filename_encoded}; size={len(decoded_data)}'
            )
            message.attach(part)

    return message



