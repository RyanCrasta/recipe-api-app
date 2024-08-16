from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True)
def send_mail_function(self):
    users = get_user_model().objects.all()
    for user in users:
        mail_subject = 'Hello celery testing'
        message = "assignment submission"
        to_email = user.email
        send_mail(subject=mail_subject, message=message, from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[to_email], fail_silently=False)

    return 'MAIL SENT DONE'
