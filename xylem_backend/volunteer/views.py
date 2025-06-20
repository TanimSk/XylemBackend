from django.conf import settings
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from .serializers import VolunteerRegistrationSerializer, VolunteerSerializer


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 6
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


class VolunteerProfileView(APIView):
    permission_classes = [AuthenticateOnlyAgent]

    def get(self, request):
        volunteer = request.user.volunteer
        serializer = VolunteerSerializer(volunteer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        volunteer = request.user.volunteer
        serializer = VolunteerSerializer(volunteer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
