from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from users.models import get_user_id_by_email
from recipe.models import get_recipe_details_by_user_id
from recipe.models import get_number_of_likes_using_recipe_id

@shared_task(bind=True)
def send_mail_function(self):
    users = get_user_model().objects.all()

    for user in users:
        mail_subject = 'Check how many people liked your recipes'
        email_message = ''
        to_email = user.email

        user_id = get_user_id_by_email(user.email)
        recipes_details = get_recipe_details_by_user_id(user_id)

        for index in range(len(recipes_details)):
            nos_of_likes = get_number_of_likes_using_recipe_id(recipes_details[index]['id'])
            if(nos_of_likes == 1):
                email_message = email_message + f"{index+1} ) Your {recipes_details[index]['title']} recipe got {nos_of_likes} like\n"
            else:
                email_message = email_message + f"{index+1} ) Your {recipes_details[index]['title']} recipe got {nos_of_likes} likes\n"

        if(len(email_message) == 0):
            email_message = "You don't have any recipes listed"

        send_mail(subject=mail_subject, message=email_message, from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[to_email], fail_silently=True)

    return 'MAIL SENT DONE'
