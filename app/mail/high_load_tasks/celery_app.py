# celery будет использоваться для загрузки больших файлов, а так же для отправки тяжелых attachments

# from celery import Celery
# import os
# import asyncio
#
# from ..schemas.request.schemas_mail_req import EmailSend
# from ..settings_mail_servers.settings_server import SettingsServer
# from ..utils_func_API import create_email_with_attachments
# from ..imap_smtp_connect.smtp_connection import get_smtp_connection, get_smtp_connection_celery
#
# # # Для Windows используем eventlet
# # import platform
# #
# # if platform.system() == 'Windows':
# #     import eventlet
# #
# #     eventlet.monkey_patch()
#
# celery = Celery(
#     "send_mail",
#     broker=f"redis://:{SettingsServer.REDIS_PASS}@{SettingsServer.REDIS_IP}:{SettingsServer.REDIS_PORT}/0",
#     backend=f"redis://:{SettingsServer.REDIS_PASS}@{SettingsServer.REDIS_IP}:{SettingsServer.REDIS_PORT}/1"
# )
#
# # Обновленная конфигурация для Windows
# celery.conf.update(
#     task_serializer='json',
#     result_serializer='json',
#     accept_content=['json'],
#     timezone='Europe/Moscow',
#     enable_utc=True,
#     task_track_started=True,
#     task_acks_late=True,
#     worker_prefetch_multiplier=1,
#     worker_pool='solo',  # Используем solo для Windows
#     # worker_pool='gevent', Используем для Linux
#     worker_concurrency=1,  # Количество green threads
#     broker_connection_retry_on_startup=True
# )
#
#
# @celery.task(bind=True, name="send_email_task")
# def send_email_task(self, email_data, mail_login):
#     print('start task')
#     try:
#         email_send = EmailSend(**email_data)
#
#         message = create_email_with_attachments(email_send, mail_login[0])
#         smtp = get_smtp_connection_celery(mail_login[1], mail_login[2])
#
#         status, response = asyncio.to_thread(smtp.send_message,message)
#         return {"status": status, "response": response}
#     except Exception as e:
#         print(f"Error in send_email_task: {str(e)}")
#         raise self.retry(exc=e, countdown=60)
