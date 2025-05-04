import os
import aiofiles
from configparser import ConfigParser


class Settings:

    def __init__(self):
        self.config = ConfigParser()

    def open_conf(self):
        conf_path = os.path.join(os.path.dirname(__file__), "config/config.ini")
        with open(conf_path, 'r', encoding='utf-8') as config_file:
            self.config.read_file(config_file)

    def write_conf(self):
        static_dir = os.path.join(os.path.dirname(__file__), "config/config.ini")
        with open(static_dir, 'r+', encoding='utf-8') as config_file:
            self.config.write(config_file)

    def get_conf(self):
        return self.config


class SettingsAsync:
    def __init__(self):
        self.config = ConfigParser()

    async def __aenter__(self):
        await self.open_conf()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.write_conf()

    async def open_conf(self):
        conf_path = os.path.join(os.path.dirname(__file__), "config/config.ini")
        async with aiofiles.open(conf_path, mode='r', encoding='utf-8') as config_file:
            contents = await config_file.read()
            self.config.read_string(contents)

    async def write_conf(self):
        static_dir = os.path.join(os.path.dirname(__file__), "config/config.ini")
        async with aiofiles.open(static_dir, mode='w', encoding='utf-8') as config_file:
            contents = self.config_to_string()
            await config_file.write(contents)

    def config_to_string(self):
        from io import StringIO
        string_io = StringIO()
        self.config.write(string_io)
        return string_io.getvalue()

    def get_conf(self):
        return self.config


async def get_settings():
    async with SettingsAsync() as settings:
        yield settings
