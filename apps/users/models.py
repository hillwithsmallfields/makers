from django.db import models

# based on https://wsvincent.com/django-custom-user-model-tutorial/

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    link_id = models.CharField(max_length=36)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'link_id']

    def __str__(self):
        return "<user " + self.username + " link " + self.link_id + ">"
