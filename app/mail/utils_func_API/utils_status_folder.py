def parse_status_folders_response(response: bytes) -> dict:
    """
    Парсит строчку b'INBOX (MESSAGES 21 RECENT 0 UNSEEN 3)' и возвращает {"messages": 21, "recent": 0,"unseen": 3}
    """
    response_str = response.decode()
    data_str = response_str.split('(', 1)[1].rstrip(')')
    data_parts = data_str.split()
    result = {}
    for i in range(0, len(data_parts), 2):
        key = data_parts[i].lower()  # Преобразуем ключ в нижний регистр
        value = int(data_parts[i + 1])  # Преобразуем значение в число
        result[key] = value
    return result
