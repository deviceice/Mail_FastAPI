# celery будет использоваться для загрузки больших файлов, а так же для отправки тяжелых attachments

# from celery import Celery

# def create_celery_app():
#     celery = Celery(
#         'tasks',
#         broker='redis://localhost:6379/0',
#         backend='redis://localhost:6379/1'
#     )
#     return celery

# celery_app = create_celery_app()
# app.state.celery = celery_app

# @celery_app.task
# def send_email_async(email_data: dict):
# pass
