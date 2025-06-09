from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    # Boolean fields to select the type of account.
    is_admin = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class MissingReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    GENDER_CHOICES = (
        ("male", "male"),
        ("female", "female"),
        ("not_specified", "not specified"),
    )
    gender = models.CharField(
        max_length=20, choices=GENDER_CHOICES, default="not_specified"
    )
    clothing_description = models.CharField(max_length=255, null=True, blank=True)
    last_seen_location = models.CharField(max_length=255, null=True, blank=True)
    last_seen_datetime = models.DateTimeField(null=True, blank=True)
    photo_url1 = models.URLField(null=True, blank=True)
    photo_url2 = models.URLField(null=True, blank=True)
    photo_url3 = models.URLField(null=True, blank=True)
    approved = models.BooleanField(default=False)

    # basic info of the person who reported
    reporter_name = models.CharField(max_length=100, null=True, blank=True)
    reporter_contact = models.CharField(max_length=100, null=True, blank=True)
    reporter_location = models.CharField(max_length=255, null=True, blank=True)
    note = models.CharField(max_length=500, null=True, blank=True)
