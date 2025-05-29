import re
from mail.utils_func_API.utils_mails import format_size, parse_bodystructure, find_attachments


async def clear_bytes_in_message_for_number(message):
    """
    Функция принимает и парсит ответ по такой структуре
    FETCH должен быть с такой структурой "(FLAGS BODY[HEADER] BODYSTRUCTURE)"
    status, msg_data_bytes = await imap.fetch(number, "(UID FLAGS BODY.PEEK[HEADER] BODYSTRUCTURE)")
    Возвращает headers_data -
    Массив сообщений [bytearray(b'Return-path: <user@ma******),bytearray(b'Return-path:*****)]
    и data_flags_attachment= [{'number': 20, 'uid': '993', 'flags': False, 'attachments': []},
    {'number': 21, 'uid': '994', 'flags': False, 'attachments': []}]
    """
    headers_data = []
    data_flags_attachment = []
    message.pop()
    uid = None
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
        # print('attachments=', attachments)
        message_dict = {}
        headers_data.append(headers)
        flags_search = flags_pattern.search(metadata)
        if flags_search:
            message_dict['number'] = int(flags_search.group(1))  # Порядковый номер
            uid = str(flags_search.group(2).decode())  # UID
            message_dict['uid'] = uid
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
    return headers_data, data_flags_attachment, uid
