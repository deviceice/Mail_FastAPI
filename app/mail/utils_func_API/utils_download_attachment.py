import os
import uuid
from typing import Any
import aiofiles
import aiofiles.os as aios
from base64io import Base64IO
import io


async def async_chunked_base64_to_temp(encoded_data: bytes, temp_dir) -> tuple[Any, str]:
    file_uuid = str(uuid.uuid4())
    save_path = temp_dir / file_uuid
    input_stream = io.BytesIO(encoded_data)
    decoder = Base64IO(input_stream)

    async with aiofiles.open(save_path, 'wb') as out_file:
        while True:
            chunk = decoder.read(64 * 1024)
            if not chunk:
                break
            await out_file.write(chunk)

    return save_path, file_uuid


async def delete_temp_file(path: str) -> None:
    try:
        await aios.remove(path)
    except Exception as e:
        pass
