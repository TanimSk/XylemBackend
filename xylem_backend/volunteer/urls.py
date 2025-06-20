from django.urls import path
from .views import VolunteerRegistrationView, VolunteerProfileView

urlpatterns = [
    path(
        "registration/",
        VolunteerRegistrationView.as_view(),
        name="volunteer_registration",
    ),
    path(
        "profile/",
        VolunteerProfileView.as_view(),
        name="volunteer_profile",
    ),
]
