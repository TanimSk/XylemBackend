from django.shortcuts import render
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from functools import wraps


# models
from administrator.models import MissingReport

# serializers
from administrator.serializers import MissingReportSerializer


# Authenticate User Only Class
class AuthenticateOnlyAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_admin:
                return True
            else:
                return False

        return False


def logged_in_only_admin(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            if user.is_admin:
                return func(self, request, *args, **kwargs)
            else:
                for field in user._meta.fields:
                    print(f"{field.name} = {getattr(user, field.name)}")
                return Response(
                    {
                        "success": False,
                        "message": "You do not have permission to access this resource.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            return Response(
                {
                    "success": False,
                    "message": "You must be logged in to access this resource.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

    return wrapper


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 500
    page_query_param = "p"


class ManageMissingReportsView(APIView):
    pagination_class = StandardResultsSetPagination

    @logged_in_only_admin
    def get(self, request, *args, **kwargs):
        if request.GET.get("id"):
            report_id = request.GET.get("id")
            try:
                report = MissingReport.objects.get(id=report_id)
            except MissingReport.DoesNotExist:
                return Response(
                    {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = MissingReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_200_OK)
        reports = MissingReport.objects.all().order_by("-last_seen_datetime")
        paginator = self.pagination_class()
        paginated_reports = paginator.paginate_queryset(reports, request)
        serializer = MissingReportSerializer(paginated_reports, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = MissingReportSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Missing report created successfully.",
                    **serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

    @logged_in_only_admin
    def put(self, request, *args, **kwargs):
        report_id = kwargs.get("id")
        try:
            report = MissingReport.objects.get(id=report_id)
        except MissingReport.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = MissingReportSerializer(report, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Missing report updated successfully.",
                    **serializer.data,
                },
                status=status.HTTP_200_OK,
            )

    @logged_in_only_admin
    def delete(self, request, *args, **kwargs):
        report_id = kwargs.get("id")
        try:
            report = MissingReport.objects.get(id=report_id)
        except MissingReport.DoesNotExist:
            return Response(
                {"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND
            )

        report.delete()
        return Response(
            {
                "success": True,
                "message": "Missing report deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
