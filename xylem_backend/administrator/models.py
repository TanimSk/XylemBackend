from django.db import models
from django.contrib.auth.models import AbstractUser
from volunteer.models import Volunteer
from django.conf import settings
import uuid
from utils.openai_text_processor import matching_score


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

    # only for scrappers
    confidence_level = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    source = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    volunteer = models.ForeignKey(
        "volunteer.Volunteer",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="missing_reports",
    )

    # on creation of the report, assign the volunteer who is nearest to the reporter's location
    def save(self, *args, **kwargs):
        if not self.volunteer:
            # Find the nearest volunteer based on reporter's location
            volunteers = Volunteer.objects.all()
            if volunteers:
                nearest_volunteer = None
                highest_score = 0

                for volunteer in volunteers:
                    if volunteer.address and self.last_seen_location:
                        score = matching_score(
                            volunteer.address, self.last_seen_location
                        )
                        print(f"{score} for volunteer {volunteer.name}")
                        if score > highest_score:
                            highest_score = score
                            nearest_volunteer = volunteer

                self.volunteer = nearest_volunteer
        super().save(*args, **kwargs)
