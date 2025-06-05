from django.shortcuts import render
from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from .serializers import VolunteerRegistrationSerializer


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 500
    page_query_param = "p"


# Authenticate User Only Class
class AuthenticateOnlyAgent(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_volunteer:
                return True
            else:
                return False

        return False


class VolunteerRegistrationView(RegisterView):
    serializer_class = VolunteerRegistrationSerializer
