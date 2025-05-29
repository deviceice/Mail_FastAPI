from mail.utils_func_API import parse_bodystructure, find_attachments


async def get_name_attachments(bodystructure):
    """
    Парсит bodystructure и взращает list в котором dicts [{"filename": text.txt, "size":213},]

    """
    bodystructure_str = bodystructure.decode('utf-8')
    idx = bodystructure_str.find('(')
    if idx != -1:
        bodystructure_str = bodystructure_str[idx:]

    parsed_bs = parse_bodystructure(bodystructure_str)
    attachments = find_attachments(parsed_bs)
    return attachments
