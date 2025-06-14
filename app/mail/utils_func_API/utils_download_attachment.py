import asyncio
import os
import tempfile

import aiofiles
import tempfile
import base64
from base64io import Base64IO
import io
from pathlib import Path

temp_dir = Path("./Mail_FastApi/app/temp")


async def async_chunked_base64_to_temp(encoded_data: bytes) -> str:
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False)
    temp_path = temp_file.name
    temp_file.close()

    # Оборачиваем входные base64-данные в поток
    input_stream = io.BytesIO(encoded_data)

    # Base64Decoder превращает base64-поток в бинарный
    decoder = Base64IO(input_stream)

    async with aiofiles.open(temp_path, 'wb') as out_file:
        while True:
            chunk = decoder.read(64 * 1024)
            if not chunk:
                break
            await out_file.write(chunk)

    return temp_path


def delete_temp_file(path: str):
    try:
        os.remove(path)
    except Exception as e:
        print(f"Error deleting temp file {path}: {e}")
