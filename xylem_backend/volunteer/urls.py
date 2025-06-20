from django.urls import path
from .views import VolunteerRegistrationView, VolunteerProfileView, ReportsView

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
    path(
        "reports/",
        ReportsView.as_view(),
        name="volunteer_reports",
    ),
]
