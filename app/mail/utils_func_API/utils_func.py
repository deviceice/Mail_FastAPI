import base64
import re
from email.header import decode_header
from fastapi import Request
import imaplib
from mail.http_exceptions.default_exception import HTTPExceptionMail
from mail.settings_mail_servers.settings_server import SettingsServer
from imapclient.imap_utf7 import encode, decode


async def get_mail_login_pam(request: Request):
    auth_header = request.headers.get("authorization")
    encoded_credentials = auth_header.split(" ")[1]
    decoded_bytes = base64.b64decode(encoded_credentials)
    decoded_credentials = decoded_bytes.decode("utf-8")
    try:
        username, password = decoded_credentials.split(":", 1)
        mail_login = username + '@' + SettingsServer.SMTP_HOST
        return mail_login
    except ValueError:
        return None


async def get_mail_login_pam_celery(request: Request):
    auth_header = request.headers.get("authorization")
    encoded_credentials = auth_header.split(" ")[1]
    decoded_bytes = base64.b64decode(encoded_credentials)
    decoded_credentials = decoded_bytes.decode("utf-8")
    try:
        username, password = decoded_credentials.split(":", 1)
        mail_login = username + '@' + SettingsServer.SMTP_HOST
        return mail_login, username, password
    except ValueError:
        return None


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


# async def parse_folders(response):
#     print(response)
#     # Возвращает все папки пользователя уже раскодированными
#     folders = []
#     for line in response:
#         if not line.startswith(b'('):
#             continue
#         line_str = line.decode()
#         parts = line_str.split()
#         folder_name = parts[-1]
#         if folder_name.startswith('"') and folder_name.endswith('"'):
#             folder_name = folder_name[1:-1]
#         folder_name = decode_name_imap_utf7(folder_name)
#         # print(folder_name)
#         # folder_name = await decode_name_ascii_utf7(folder_name)
#         folders.append(folder_name)
#     return folders

def parse_folders(response):
    folders = []
    for line in response:
        if not line.startswith(b'('):
            continue
        line_str = line.decode('utf-8')
        match = re.search(r'\) "." "(.*?)"$', line_str)
        if not match:
            match = re.search(r'\) "." ([^"]+)$', line_str)
        if match:
            encoded_name = match.group(1)
            try:
                folder_name = decode(encoded_name)
            except Exception as e:
                folder_name = encoded_name
            folder_name = decode_name_imap_utf7(folder_name)
            folders.append(folder_name)
    return folders


def get_decode_header_subject(message):
    # Возвращает декодированный Subject из Header
    if message["Subject"] is None:
        return ''
    encoding = decode_header(message["Subject"])[0][1]
    if encoding is None:
        return decode_header(message["Subject"])[0][0]
    else:
        return decode_header(message["Subject"])[0][0].decode(encoding)


# async def decode_name_ascii_utf7(name: str) -> str:
#     return name.encode('ascii').decode('utf-7')


# async def encode_name_utf7_ascii(name: str) -> str:
#     return name.encode('utf-7').decode('ascii')


def decode_name_imap_utf7(s: str) -> str:
    def decode_match(m):
        b64 = m.group(1)
        if not b64:
            return '&'
        b64 += '=' * (-len(b64) % 4)  # padding
        decoded = base64.b64decode(b64.replace(',', '/'))
        return decoded.decode('utf-16-be')

    return re.sub(r'&([A-Za-z0-9+,]*?)-', decode_match, s)


def encode_name_imap_utf7(s: str) -> str:
    result = []
    buffer = ""

    def flush_buffer():
        nonlocal buffer
        if buffer:
            utf16 = buffer.encode('utf-16-be')
            b64 = base64.b64encode(utf16).decode('ascii').replace('/', ',')
            result.append('&' + b64.rstrip('=') + '-')
            buffer = ""

    for ch in s:
        code = ord(ch)
        if 0x20 <= code <= 0x7E and ch != '&':
            flush_buffer()
            result.append(ch)
        elif ch == '&':
            flush_buffer()
            result.append('&-')
        else:
            buffer += ch

    flush_buffer()
    return ''.join(result)
