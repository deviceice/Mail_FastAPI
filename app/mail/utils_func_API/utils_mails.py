import re
from mail.utils_func_API.utils_func import *
from typing import Union, Optional, List, Dict, Sequence
from loguru import logger
from email.utils import decode_rfc2231
import email
import urllib.parse


async def get_elements_inbox_uid(arr, last_uid=None, limit=20):
    """
    Возвращает последнии N=limit elem из list или N=limit предыдущих elem начиная после last_uid
    """
    if last_uid is None or len(last_uid) == 0:
        return arr[-limit:]
    else:
        try:
            index = arr.index(last_uid)
        except ValueError:
            return []

        return arr[max(0, index - limit):index]


async def clear_bytes_in_message(message):
    """
    Функция принимает и парсит ответ по такой структуре
    FETCH должен быть с такой структурой "(FLAGS RFC822.HEADER BODYSTRUCTURE)"
    status, message = await imap.uid("FETCH", ",".join(mails_uids), "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
    Возвращает headers_data -
    Массив сообщений [bytearray(b'Return-path: <user@ma******),bytearray(b'Return-path:*****)]
    и data_flags_attachment= [{'number': 20, 'uid': '993', 'flags': False, 'attachments': []},
    {'number': 21, 'uid': '994', 'flags': False, 'attachments': []}]
    """
    headers_data = []
    data_flags_attachment = []
    message.pop()

    flags_pattern = re.compile(rb'(\d+) FETCH \(UID (\d+) FLAGS \((.*?)\) RFC822\.HEADER')

    for i in range(0, len(message), 3):
        metadata = message[i]
        headers = message[i + 1]
        bodystructure = message[i + 2]
        bodystructure_str = bodystructure.decode('utf-8')
        idx = bodystructure_str.find('(')
        if idx != -1:
            bodystructure_str = bodystructure_str[idx:]

        parsed_bs = parse_bodystructure(bodystructure_str)
        attachments = find_attachments(parsed_bs)
        message_dict = {}
        headers_data.append(headers)
        flags_search = flags_pattern.search(metadata)
        if flags_search:
            message_dict['number'] = int(flags_search.group(1))  # Порядковый номер
            message_dict['uid'] = str(flags_search.group(2).decode())  # UID
            flags = flags_search.group(3).decode().split()
            message_dict['flags'] = True if '\\Flagged' in flags else False
        else:
            # Доработать
            pass
            # continue

        if attachments:
            message_dict['attachments'] = attachments
        else:
            message_dict['attachments'] = []
        data_flags_attachment.append(message_dict)
    return headers_data, data_flags_attachment


def tokenize(s):
    pattern = r'\(|\)|"[^"]*"|[^\s()]+'
    tokens = re.findall(pattern, s)
    return tokens


def parse(tokens):
    token = tokens.pop(0)
    if token == '(':
        lst = []
        while tokens[0] != ')':
            lst.append(parse(tokens))
        tokens.pop(0)  # Убираем ')'
        return lst
    elif token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    elif token == 'NIL':
        return None
    else:
        return token


def parse_bodystructure(s):
    tokens = tokenize(s)
    return parse(tokens)


def find_attachments(bodystructure):
    attachments = []

    def _walk(node):
        if isinstance(node, list):
            # Проверяем, есть ли у части ("attachment" (...))
            for item in node:
                if (isinstance(item, list) and len(item) > 0
                        and item[0] == "attachment"):
                    params = item[1]
                    filename = None
                    size = None
                    for i in range(0, len(params), 2):
                        key = params[i]
                        val = params[i + 1]
                        if key == "filename*" or key == "filename":
                            filename = val
                        elif key == "size":
                            size = val
                    if filename is None:
                        filename_decoded = 'None'
                    else:
                        charset, language, encoded_value = decode_rfc2231(filename)
                        filename_decoded = urllib.parse.unquote(encoded_value)
                    attachments.append({
                        "filename": filename_decoded,
                        "size": str(size) if size else None
                    })
                else:
                    _walk(item)

    _walk(bodystructure)
    return attachments


async def get_mails_uids_unseen(messages, messages_unseen):
    mails_uids = messages[0].decode().split()
    total_message = len(mails_uids)
    mails_uids_unseen = set(messages_unseen[0].decode().split())
    return mails_uids, mails_uids_unseen, total_message


async def get_message_struct(mail_uid, mails_uids_unseen, message, options):
    if mails_uids_unseen is None:
        mails_uids_unseen = [mail_uid]
    try:
        options_uid = options["uid"]
    except KeyError:
        logger.error(f'ОШИБКА С ПИСЬМОМ возможно баг{mail_uid, message, options}')
        options_uid = '0'
    return {
        "uid": mail_uid,
        # "uid_last_ref": mail_uid,
        "message_id": message.get("Message-ID", "").strip('<>'),
        "from": message["From"] if message["From"] else '',
        "to": message['To'].split(',') if message['To'] else [],
        "subject": await get_decode_header_subject(message),
        "date": message["Date"] if message["Date"] else '',
        "is_read": True if mail_uid not in mails_uids_unseen else False,
        "flags": options['flags'] if mail_uid == options_uid else False,
        "attachments": options['attachments'] if mail_uid == options_uid else [],
        # "references": message['References'] if message['References'] else '',
        "references": message.get("References", "").strip('<>'),
        "mails_reference": [],
    }


async def get_message_struct_websocket(mail_uid, message, options):
    return {
        "uid": mail_uid,
        "message_id": message.get("Message-ID", "").strip('<>'),
        "from": message["From"] if message["From"] else '',
        "to": message['To'].split(',') if message['To'] else '',
        "subject": await get_decode_header_subject(message),
        "date": message["Date"] if message["Date"] else '',
        "is_read": False,
        "flags": options['flags'] if mail_uid == options['uid'] else False,
        "attachments": options['attachments'] if mail_uid == options['uid'] else [],
        "references": message.get("References", "").strip('<>'),
        "mails_reference": [],
    }


async def get_message_ref_struct(mail_uid_reference, mails_uids_unseen, message_reference, option_reference):
    return {
        "uid": mail_uid_reference,
        "message_id": message_reference.get("Message-ID", "").strip('<>'),
        "from": message_reference["From"] if message_reference["From"] else '',
        "to": message_reference['To'].split(',') if message_reference['To'] else '',
        "subject": await get_decode_header_subject(message_reference),
        "date": message_reference["Date"] if message_reference["Date"] else '',
        "is_read": True if mail_uid_reference not in mails_uids_unseen else False,
        "flags": option_reference['flags'] if mail_uid_reference == option_reference['uid'] else False,
        "attachments": option_reference['attachments'] if mail_uid_reference == option_reference[
            'uid'] else [],
    }


async def sort_emails(emails):
    emails_sorted = sorted(emails, key=lambda x: int(x['uid_last_ref']), reverse=True)
    return emails_sorted
