from celery import shared_task
from time import sleep

from django.core.mail import send_mail


@shared_task
def sleepy(duration):
    sleep(duration)
    return None
@shared_task
def send_email_task(subject,message,sender,recipients):
    sleep(30)
    send_mail(
        subject,message,sender,recipients
    )
    return None