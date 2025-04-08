from mail.support_func_API.support_func import *
import email


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

        # если есть вложения, добавит имя, файлы и размер
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


# async def get_references(imap, message_id: str, mails_uids_unseen: list) -> list:
#     search_criteria = f'HEADER References "{message_id}"'
#     status_reference, references_data = await imap.uid_search(search_criteria)
#     references_uids = references_data[0].decode().split() if status_reference == 'OK' else []
#     status_message_reference, msg_data_reference_bytes = await imap.uid("FETCH", ",".join(references_uids),
#                                                                         "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
#
#     msg_data_referances, options_references = await clear_bytes_in_message(msg_data_reference_bytes)
#     references_message = []
#     for mail_uid_reference, msg_data_reference, option_reference in zip(references_uids,
#                                                                         msg_data_referances,
#                                                                         options_references):
#         # print('msg_data_reference', msg_data_reference, option_reference)
#         message_reference = email.message_from_bytes(msg_data_reference)
#         # subject_reference = await get_decode_header_subject(message_reference)
#         message_reference_id = message_reference.get("Message-ID", "").strip('<>')
#         # mail_uid_reference.append(mail_uid_reference)
#         message = {
#             "uid": mail_uid_reference,
#             "message_id": message_reference_id,
#             "from": message_reference["From"] if message_reference["From"] else '',
#             "to": message_reference['To'].split(',') if message_reference['To'] else '',
#             "subject": await get_decode_header_subject(message_reference),
#             "date": message_reference["Date"] if message_reference["Date"] else '',
#             "is_read": True if mail_uid_reference not in mails_uids_unseen else False,
#             # "mails_referance": [],
#             "flags": option_reference['flags'] if mail_uid_reference == option_reference['uid'] else False,
#             "attachments": option_reference['attachments'] if mail_uid_reference == option_reference[
#                 'uid'] else [],
#         }
#         references_message.append(message)
#     return references_message
