from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Boolean fields to select the type of account.
    is_admin = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)

    def __str__(self):
        return self.username
