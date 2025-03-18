import base64
import binascii
import re

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

from email.header import decode_header
from mail.schemas.request_schemas import *


async def append_inbox_message_in_sent(message, imap):
    await imap.append(message_bytes=message.as_bytes(), mailbox='Sent', flags='\\Seen', )


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


async def clear_bytes_in_message(message):
    # Функция возвращает массив с сообщениями в байта, и массива с флагами и вложениями(если есть) уже в читаемоем формате
    headers_data = []
    data_flags_attachment = []
    message.pop()

    flags_pattern = re.compile(rb'(\d+) FETCH \(UID (\d+) FLAGS \((.*?)\) RFC822\.HEADER')
    attachment_pattern = re.compile(
        rb'\(["\']?attachment["\']?\s+\(["\']?filename["\']?\s+["\']([^"\']+)["\']\s+["\']?size["\']?\s+["\']?(\d+)["\']?\)')

    for i in range(0, len(message), 3):
        metadata = message[i]
        headers = message[i + 1]
        bodystructure = message[i + 2]
        message_dict = {}
        headers_data.append(headers)
        flags_search = flags_pattern.search(metadata)
        bodystructure_search = attachment_pattern.findall(bodystructure)

        if flags_search:
            message_dict['number'] = int(flags_search.group(1))  # Порядковый номер
            message_dict['uid'] = str(flags_search.group(2).decode())  # UID
            flags = flags_search.group(3).decode().split()
            message_dict['flags'] = True if '\\Flagged' in flags else False
        else:
            # Доработать
            pass
            # continue

        # если есть вложения, добавит имя файлы и размерl
        parsed_attachments = []
        if bodystructure_search:
            parsed_attachments = [
                {"filename": filename.decode(), "size": await format_size(int(size.decode()))}
                for filename, size in bodystructure_search
            ]
            message_dict['attachments'] = parsed_attachments
        else:
            message_dict['attachments'] = parsed_attachments
        data_flags_attachment.append(message_dict)
    return headers_data, data_flags_attachment


async def get_elements_inbox_uid(arr, last_uid=None, limit=20):
    # Возвращает последнии 10 uids сообщений из списка или 10 предыдущих uids сообщений от last_uid
    if last_uid is None or len(last_uid) == 0:
        return arr[-limit:]
    else:
        try:
            index = arr.index(last_uid)
        except ValueError:
            return []

        return arr[max(0, index - limit):index]


async def get_email_body(msg):
    # Возвращает body из сообщения
    if msg.is_multipart():
        for part in msg.get_payload():
            body = await get_email_body(part)
            if body:
                return body
    else:
        if msg.get_content_type() == "text/plain":
            payload = msg.get_payload(decode=True)
            if payload:
                return payload.decode("utf-8", errors="ignore")
    return None


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


async def create_email_with_attachments(email: EmailSend):
    # создает MIMEMultipart сообщение с вложенными attachments либо без них
    message = MIMEMultipart()
    message["From"] = "user@mail.palas"  # жестко пока для теста
    message["To"] = email.to if type(email.to) == str else ", ".join(email.to)
    message["Subject"] = email.subject
    message["References"] = f'<{email.referance}>' if email.referance else None
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


async def decode_bytearray(string: bytearray):
    base64_str = string.decode().strip()
    try:
        decoded_bytes = base64.b64decode(base64_str)
    except binascii.Error:
        return base64_str
    return decoded_bytes.decode('utf-8')


async def get_name_attachments(bodystructure):
    attachment_pattern = re.compile(
        rb'\(["\']?attachment["\']?\s+\(["\']?filename["\']?\s+["\']([^"\']+)["\']\s+["\']?size["\']?\s+["\']?(\d+)["\']?\)')

    bodystructure_search = attachment_pattern.findall(bodystructure)
    # если есть вложения, добавит имя файлы и размерl
    parsed_attachments = []
    if bodystructure_search:
        parsed_attachments = [
            {"filename": filename.decode(), "size": await format_size(int(size.decode()))}
            for filename, size in bodystructure_search
        ]
    return parsed_attachments
