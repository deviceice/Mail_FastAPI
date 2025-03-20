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


# async def create_email_with_attachments(email: EmailSend):
#     """
#     Cоздает MIMEMultipart сообщение с вложенными attachments либо без них, для отправки почты
#     """
#     message = MIMEMultipart()
#     message["From"] = "user@mail.palas"  # жестко пока для теста
#     message["To"] = email.to if type(email.to) == str else ", ".join(email.to)
#     message["Subject"] = email.subject
#     message["References"] = f'<{email.referance}>' if email.referance else None
#     print(email.body)
#     text = email.body.encode("utf-8")
#     print(text)
#     # message.attach(MIMEText(email.body, "plain", _charset="utf-8"))
#     # text_part = MIMEText(libmail.message(email.body))
#     text_part = MIMEText(email.body, "plain", "utf-8")
#     text_part.set_charset("utf-8")
#     text_part.replace_header("Content-Transfer-Encoding", "quoted-printable")
#     message.attach(text_part)
#     for attachment in email.attachments:
#         part = MIMEBase("application", "octet-stream")
#         decoded_data = base64.b64decode(attachment.file)
#         part.set_payload(decoded_data)
#         encoders.encode_base64(part)
#         part.add_header(
#             "Content-Disposition",
#             f"attachment; filename={attachment.filename}; size={str(len(decoded_data))}"
#         )
#         message.attach(part)
#     return message
# async def create_email_with_attachments(email: EmailSend):
#     """
#     Создает MIMEMultipart сообщение с вложенными attachments либо без них, для отправки почты.
#     """
#     # Создаем сообщение с политикой SMTP
#     message = MIMEMultipart(policy=policy.SMTP)
#
#     # Заголовки письма
#     message["From"] = "user@mail.palas"  # Жестко для теста
#     message["To"] = email.to if isinstance(email.to, str) else ", ".join(email.to)
#     message["Subject"] = email.subject
#     message["References"] = f'<{email.referance}>' if email.referance else None
#
#
#     # Создаем текстовую часть вручную
#     text_part = MIMEText(email.body, "plain", "utf-8")
#     message.attach(text_part)
#
#     # Добавляем вложения
#     for attachment in email.attachments:
#         part = MIMEBase("application", "octet-stream")
#         decoded_data = base64.b64decode(attachment.file)
#         part.set_payload(decoded_data)
#         encoders.encode_base64(part)
#         part.add_header(
#             "Content-Disposition",
#             f"attachment; filename={attachment.filename}; size={str(len(decoded_data))}"
#         )
#         message.attach(part)
#
#     print(message)
#     return message

async def create_email_with_attachments(email: EmailSend):
    """
    Создает MIMEMultipart сообщение с вложенными attachments либо без них, для отправки почты.
    """
    # Создаем сообщение с политикой SMTPUTF8
    message = MIMEMultipart()

    # Заголовки письма
    message["From"] = "user@mail.palas"  # Жестко для теста
    message["To"] = email.to if isinstance(email.to, str) else ", ".join(email.to)
    message["Subject"] = email.subject
    message["References"] = f'<{email.referance}>' if email.referance else None


    # Создаем текстовую часть вручную
    message.attach(MIMEText(email.body, "plain"))



    # Добавляем вложения
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

    print(message.as_string())  # Для проверки результата
    time.sleep(30)
    return message