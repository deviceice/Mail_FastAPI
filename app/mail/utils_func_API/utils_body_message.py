import asyncio
from email import policy
from email.parser import BytesParser
import base64
import quopri
from email.utils import parsedate_to_datetime
from urllib.parse import unquote

from mail.http_exceptions.default_exception import HTTPExceptionMail
from mail.utils_func_API import parse_bodystructure, find_attachments


async def get_name_attachments(bodystructure):
    """
    Парсит bodystructure и взращает list в котором dicts [{"filename": text.txt, "size":213},]

    """
    bodystructure_str = bodystructure.decode('utf-8')
    idx = bodystructure_str.find('(')
    if idx != -1:
        bodystructure_str = bodystructure_str[idx:]

    parsed_bs = await asyncio.to_thread(parse_bodystructure, bodystructure_str)
    attachments = await asyncio.to_thread(find_attachments, parsed_bs)
    return attachments


async def parse_email_body(imap, uid):
    status, response = await imap.uid("FETCH", uid, "(BODY.PEEK[])")
    if status != 'OK' or len(response) < 2:
        raise HTTPExceptionMail.MESSAGE_NOT_FOUND_404

    raw_email = response[1]
    msg = BytesParser(policy=policy.default).parsebytes(raw_email)

    body_parts = []
    attachments = []

    def decode_payload(part):
        payload = part.get_payload(decode=True)
        charset = part.get_content_charset() or 'utf-8'
        try:
            return payload.decode(charset)
        except Exception:
            return payload.decode('utf-8', errors='replace')

    def format_headers_nice(headers):
        date_str = "Не указана"
        if 'Date' in headers:
            try:
                dt = parsedate_to_datetime(headers['Date'])
                date_str = dt.strftime("%a %H:%M")
            except:
                date_str = headers['Date']

        fields = [
            ("Тема", headers.get('Subject', 'Без темы')),
            ("От", headers.get('From', 'Не указан')),
            ("Кому", headers.get('To', 'Не указан')),
            ("Дата", date_str)
        ]

        return "\n".join([f"{name}:\t{value}" for name, value in fields])

    def process_part(part, depth=0):
        content_type = part.get_content_type()
        content_disposition = part.get("Content-Disposition", "")
        filename = part.get_filename()

        # Вложения
        if "attachment" in content_disposition or filename:
            if filename and filename.startswith("UTF-8''"):
                filename = unquote(filename[7:])
            attachments.append({
                "filename": filename or f"attachment_{len(attachments) + 1}",
                "type": content_type,
                "size": str(len(part.get_payload(decode=True) or b""))
            })
            return

        # Текстовая часть
        if content_type in ("text/plain", "text/html") and "attachment" not in content_disposition:
            text = decode_payload(part)
            body_parts.append(text)
            return

        # Вложенное письмо (.eml)
        if content_type == "message/rfc822":
            nested_msg = part.get_payload(0) if part.is_multipart() else part
            nested_headers = dict(nested_msg.items())
            nested_header_text = format_headers_nice(nested_headers)
            nested_body = []

            if nested_msg.is_multipart():
                for nested_part in nested_msg.walk():
                    if nested_part.get_content_type().startswith("text/"):
                        nested_body.append(decode_payload(nested_part))
            else:
                nested_body.append(decode_payload(nested_msg))

            formatted_nested = f"\n\n--- Вложенное письмо ---\n{nested_header_text}\n\n{''.join(nested_body)}\n--- Конец вложенного письма ---"
            body_parts.append(formatted_nested)

            attachments.append({
                "filename": filename or f"nested_{len(attachments) + 1}.eml",
                "type": content_type,
                "size": str(len(part.get_payload(decode=True) or b""))
            })

    # Обход структуры
    if msg.is_multipart():
        for part in msg.walk():
            process_part(part)
    else:
        process_part(msg)

    return {
        "body": "\n".join(body_parts).strip(),
        "attachments": [a for a in attachments if not a["filename"].endswith('.eml')],
        "headers": dict(msg.items())
    }

