from asgiref.sync import async_to_sync
from celery import Celery

from src.mail import create_message, mail

celery_app = Celery('tasks')

celery_app.config_from_object('src.config')


@celery_app.task
def send_email_tsk(recipients: list[str], subject: str, body: str):
    message = create_message(recipients=recipients, subject=subject, body=body)
    async_to_sync(mail.send_message)(message)


# * To run the Celery worker, execute the following command:
# celery -A src.celery_tasks.celery_app worker
# * To run Flower for monitoring, execute the following command:
# celery -A src.celery_tasks.celery_app flower
