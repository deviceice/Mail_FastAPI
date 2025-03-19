from mail.support_func_API.support_func import *


async def decode_bytearray_body(string: bytearray):
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
    # если есть вложения, добавит имя файлы и размер
    parsed_attachments = []
    if bodystructure_search:
        parsed_attachments = [
            {"filename": filename.decode(), "size": await format_size(int(size.decode()))}
            for filename, size in bodystructure_search
        ]
    return parsed_attachments
