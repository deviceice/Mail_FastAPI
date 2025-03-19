from mail.support_func_API.support_func import *


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
