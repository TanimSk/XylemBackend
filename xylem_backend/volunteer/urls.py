from django.urls import path
from .views import VolunteerRegistrationView

urlpatterns = [
    path(
        "registration/",
        VolunteerRegistrationView.as_view(),
        name="volunteer_registration",
    ),
]
