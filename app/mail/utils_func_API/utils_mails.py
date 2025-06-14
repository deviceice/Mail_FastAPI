import asyncio
import re
from mail.utils_func_API.utils_func import *
from typing import Union, Optional, List, Dict, Sequence, Any
from loguru import logger
from email.utils import decode_rfc2231
import email
import urllib.parse


def get_elements_inbox_uid(arr, last_uid=None, limit=20):
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


def clear_bytes_in_message(message):
    """
    Парсим fetch ответ в виде списка с разной глубиной.
    Ищем заголовки, флаги, UID и attachments.
    """

    headers_data = []
    data_flags_attachment = []

    # Регулярка для начала блока с UID и FLAGS
    fetch_start_pattern = re.compile(rb'(\d+) FETCH \(UID (\d+) FLAGS \((.*?)\) RFC822\.HEADER')

    current_block = []
    current_metadata = None

    def process_block(block):
        # Обработка одного блока сообщений
        # блок — список байтовых строк, минимум 2 (метаданные + заголовки), потом остальные
        if not block:
            return

        metadata = block[0]
        headers = block[1]
        # Остальные — предполагаем bodystructure или вложения
        bodystructure_parts = block[2:]

        bodystructure_str = b''.join(bodystructure_parts).decode('utf-8', errors='ignore')
        idx = bodystructure_str.find('(')
        if idx != -1:
            bodystructure_str = bodystructure_str[idx:]
        else:
            bodystructure_str = ''

        parsed_bs = parse_bodystructure(bodystructure_str)
        attachments = find_attachments(parsed_bs)

        message_dict = {}

        flags_search = fetch_start_pattern.search(metadata)
        if flags_search:
            message_dict['number'] = int(flags_search.group(1))
            uid = str(flags_search.group(2).decode())
            message_dict['uid'] = uid
            flags = flags_search.group(3).decode().split()
            message_dict['flags'] = True if '\\Flagged' in flags else False
        else:
            # Нет метаданных — игнорируем или логируем
            return

        if attachments:
            message_dict['attachments'] = attachments
        else:
            message_dict['attachments'] = []

        headers_data.append(headers)
        data_flags_attachment.append(message_dict)

    for line in message:
        # Если встретили начало нового блока (новое сообщение)
        if fetch_start_pattern.match(line):
            if current_block:
                process_block(current_block)
            current_block = [line]
        else:
            current_block.append(line)

    if current_block:
        process_block(current_block)

    if data_flags_attachment:
        return headers_data, data_flags_attachment, data_flags_attachment[-1]['uid']
    else:
        return headers_data, data_flags_attachment, None


def tokenize(arg):
    """
    Обрезает по регулярному выражению
    """
    pattern = r'\(|\)|"[^"]*"|[^\s()]+'
    tokens = re.findall(pattern, arg)
    return tokens


def parse(tokens):
    """
    Обрезает после до нужных данных после tokens
    """
    token = tokens.pop(0)
    if token == '(':
        lst = []
        try:
            while tokens[0] != ')':
                lst.append(parse(tokens))
        except IndexError:
            pass
        try:
            tokens.pop(0)  # Убираем ')'
        except IndexError:
            pass
        return lst
    elif token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    elif token == 'NIL':
        return None
    else:
        return token


def parse_bodystructure(bodystructure_str):
    """
    Парсинг str bodystructure
    """
    tokens = tokenize(bodystructure_str)
    data = parse(tokens)
    return data


def find_attachments(bodystructure):
    """
    Ищет вложения в уже распрашенной bodystructure
    """
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


def get_mails_uids_unseen(messages, messages_unseen):
    """
    Возвращает списки с uids всех сообщений, и непрочитанных сообщений, а так же колличество сообщейний
    """
    mails_uids = messages[0].decode().split()
    total_messages = len(mails_uids)
    mails_uids_unseen = set(messages_unseen[0].decode().split())
    total_unseen_messages = len(mails_uids_unseen)
    return mails_uids, mails_uids_unseen, total_messages, total_unseen_messages


def get_message_struct(mail_uid, mails_uids_unseen, message, options):
    if mails_uids_unseen is None:
        mails_uids_unseen = [str(mail_uid)]
    try:
        options_uid = options["uid"]
    except KeyError:
        logger.error(f'ОШИБКА С ПИСЬМОМ возможно баг{mail_uid, message, options}')
        options_uid = '0'
    references_str = message.get("References", "").strip()
    if references_str:
        refs = [r for r in references_str.split() if r.strip()]
        last_ref = refs[-1].strip('<>') if refs else ''
    else:
        last_ref = ''

    test = message.get("Message-ID", "").strip('<>')
    # if test =="":
    #     print(message)
    # print('test=', message.get("Message-ID", "").strip('<>'))
    return {
        "uid": mail_uid,
        "message_id": message.get("Message-ID", "").strip('<>'),
        "from": message["From"] if message["From"] else '',
        "to": message['To'].split(',') if message['To'] else [],
        "subject": get_decode_header_subject(message),
        "date": message["Date"] if message["Date"] else '',
        "is_read": True if str(mail_uid) not in mails_uids_unseen else False,
        "flags": options['flags'] if str(mail_uid) == str(options_uid) else False,
        "attachments": options['attachments'] if str(mail_uid) == str(options_uid) else [],
        "references": last_ref,
        "mails_reference": [],
    }


def parse_thread_response(raw_response: bytes):
    """
    Парсит ответ от imap если это дерево uids await imap.uid('THREAD', 'REFERENCES UTF-8 ALL')
    """
    raw = raw_response.decode().strip()
    raw = re.sub(r'Thread completed.*', '', raw)
    tokens = re.findall(r'\(|\)|\d+', raw)

    stack = []
    current = []
    for token in tokens:
        if token == '(':
            stack.append(current)
            current = []
        elif token == ')':
            last = current
            current = stack.pop()
            current.append(last)
        else:
            current.append(int(token))
    return current


def flatten_thread(thread):
    """
    Cобирает дерево uids из lists в одинарный list
    """
    uids = []
    if isinstance(thread, list):
        for item in thread:
            uids.extend(flatten_thread(item))
    else:
        uids.append(thread)
    return uids


def get_max_uid_in_thread(email):
    """
    Вычисляет максимальный uid в reference письмах
    """
    max_uid = email['uid']
    for child in email.get('mails_reference', []):
        max_uid = max(max_uid, get_max_uid_in_thread(child))
    return max_uid


def build_email_tree_by_references(messages_dict):
    """
    Строит дерево писем
    """
    msgid_map = {msg['message_id']: msg for msg in messages_dict.values()}
    uid_map = {msg['uid']: msg for msg in messages_dict.values()}
    child_to_parent = {}

    for msg in messages_dict.values():
        msg['mails_reference'] = []

    for msg in messages_dict.values():
        ref_id = msg.get('references')
        if ref_id and ref_id in msgid_map:
            parent = msgid_map[ref_id]
            parent['mails_reference'].append(msg)
            child_to_parent[msg['uid']] = parent['uid']

    root_emails = [msg for uid, msg in uid_map.items() if uid not in child_to_parent]

    return root_emails


def get_root_threads_slice(thread_tree, limit=20, last_uid=None):
    """
    Функция получает дерево листов с uids писем, и вырезает нужный отрезок
    """
    root_uids = [elem[0] if isinstance(elem, list) else elem for elem in thread_tree]

    if last_uid is not None:
        try:
            index = root_uids.index(int(last_uid))
        except ValueError:
            # Если не нашли last_uid — взять последние limit
            return thread_tree[-limit:]

        # Вычисляем границы среза: от (index - limit) до index
        start = max(0, index - limit)
        end = index
        return thread_tree[start:end]
    else:
        # Если last_uid нет — вернуть последние limit
        return thread_tree[-limit:]


def subject_filter(filter, mails):
    if filter:
        subject_filter_lower = filter.lower()
        mails = [
            mail for mail in mails
            if subject_filter_lower in (mail.get('subject') or '').lower()
        ]
    return mails
