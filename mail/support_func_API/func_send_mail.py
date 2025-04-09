import time

from mail.support_func_API.support_func import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders, policy
import base64


async def append_inbox_message_in_sent(message, imap):
    """
    Копирует сообщение в папку Отправленные с Флагом прочитано
    """
    await imap.append(message_bytes=message.as_bytes(), mailbox='Sent', flags='\\Seen', )


async def create_email_with_attachments(email: EmailSend):
    """
    Создает MIMEMultipart сообщение с вложенными attachments либо без них, для отправки почты.
    """
    message = MIMEMultipart()
    message["From"] = "user@mail.palas"  # Жестко для теста
    message["To"] = email.to if isinstance(email.to, str) else ", ".join(email.to)
    message["Subject"] = email.subject
    message["References"] = f'<{email.reference}>' if email.reference else None
    message.attach(MIMEText(email.body, "plain"))
    for attachment in email.attachments:
        part = MIMEBase("application", "octet-stream")
        decoded_data = base64.b64decode(attachment.file)
        part.set_payload(decoded_data)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={attachment.filename}; size={str(len(decoded_data))}"
        )
        message.attach(part)

    return message
