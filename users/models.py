from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from recipe.models import Recipe
from .managers import CustomUserManager
from django.core.exceptions import ObjectDoesNotExist

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bookmarks = models.ManyToManyField(Recipe, related_name='bookmarked_by')
    avatar = models.ImageField(upload_to='avatar', blank=True)
    bio = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.username

def get_user_id_by_email(email):
    try:
        user = CustomUser.objects.get(email=email)
        return user.id
    except ObjectDoesNotExist:
        return None
    except CustomUser.MultipleObjectsReturned:
        raise ValueError("Multiple users found with the same email")
