# celery будет использоваться для загрузки больших файлов, а так же для отправки тяжелых attachments

from celery import Celery
import os

from ..settings_mail_servers.settings_server import SettingsServer

celery = Celery(
    "send_mail",
    broker=f"redis://:{SettingsServer.REDIS_PASS}@{SettingsServer.REDIS_IP}:{SettingsServer.REDIS_PORT}/0",
    backend=f"redis://:{SettingsServer.REDIS_PASS}@{SettingsServer.REDIS_IP}:{SettingsServer.REDIS_PORT}/1"
)


celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Europe/Moscow',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1  # Важно для больших задач
)