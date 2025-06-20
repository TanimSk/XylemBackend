from django.conf import settings
from django.shortcuts import render
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from utils.openai_text_processor import process_text_with_openai, summarize_text
from datetime import datetime

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

    # @logged_in_only_admin
    def get(self, request, *args, **kwargs):
        if request.query_params.get("action") == "search":
            if request.query_params.get("key") == settings.BOT_API_KEY:
                name = request.query_params.get("name")
                age = request.query_params.get("age")
                age = int(age) if age else None
                gender = request.query_params.get("gender")
                last_seen_location = request.query_params.get("last_seen_location")
                clothing_description = request.query_params.get("clothing_description")
                last_seen_date = request.query_params.get("last_seen_date")
                last_seen_date = (
                    datetime.strptime(last_seen_date, "%Y-%m-%d")
                    if last_seen_date
                    else None
                )

                reports = MissingReport.objects.filter(
                    # name
                    **({"name__icontains": name} if name else {}),
                    # age
                    **({"age": age} if age is not None else {}),
                    # gender
                    **({"gender": gender} if gender is not None else {}),
                    # last_seen_location
                    **(
                        {"last_seen_location__icontains": last_seen_location}
                        if last_seen_location
                        else {}
                    ),
                    # clothing_description
                    **(
                        {"clothing_description__icontains": clothing_description}
                        if clothing_description
                        else {}
                    ),
                    # last_seen_datetime
                    **(
                        {"last_seen_datetime__date": last_seen_date}
                        if last_seen_date
                        else {}
                    ),
                )

                # return
                paginator = self.pagination_class()
                paginated_reports = paginator.paginate_queryset(reports, request)
                serializer = MissingReportSerializer(paginated_reports, many=True)
                return paginator.get_paginated_response(serializer.data)

        # check if authenticated user is admin
        if not (request.user and request.user.is_authenticated):
            reports = MissingReport.objects.filter(approved=True, confidence_level__gte=0.5).order_by(
                "-created_at"
            )
            # return
            paginator = self.pagination_class()
            paginated_reports = paginator.paginate_queryset(reports, request)
            serializer = MissingReportSerializer(paginated_reports, many=True)
            return paginator.get_paginated_response(serializer.data)

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
        reports = MissingReport.objects.all().order_by("-created_at")
        paginator = self.pagination_class()
        paginated_reports = paginator.paginate_queryset(reports, request)
        serializer = MissingReportSerializer(paginated_reports, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if request.query_params.get(
            "key"
        ) == settings.BOT_API_KEY and not request.query_params.get("source"):
            print("Received request from Telegram bot")
            data = json.loads(request.body.decode("utf-8"))
            chat_id = data.get("message", {}).get("chat", {}).get("id")
            user_text = data.get("message", {}).get("text", "")
            from_user = data.get("message", {}).get("from", {})
            chat = data.get("message", {}).get("chat", {})
            chat_id = chat["id"]

            # Prevent loop: don't reply to messages sent by the bot itself
            if from_user.get("id") == settings.TG_BOT_TOKEN:
                return Response({"ok": True, "skipped": "Message from self"})

            # Optionally: only handle group messages
            if chat.get("type") != "group" and chat.get("type") != "supergroup":
                return Response({"ok": True, "skipped": "Not a group message"})

            # Send reply
            requests.post(
                f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "Processing your message, please wait...",
                },
            )

            json_data = process_text_with_openai(user_text)
            print("Extracted JSON data:", json_data)
            if not json_data:
                reply_text = (
                    "Sorry, I couldn't extract any information from your message."
                )
            else:
                # Save the missing report
                serializer = MissingReportSerializer(data=json_data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save(source="telegram")
                    reply_text = "Missing report created successfully."
                else:
                    reply_text = "Failed to create missing report. Please check the format of your message."

            # Send reply
            requests.post(
                f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": reply_text,
                },
            )

            requests.post(
                f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"Summary of the report:\n```{summarize_text(json_data)}```",
                    "parse_mode": "MarkdownV2",
                },
            )

            return Response(
                {
                    "ok": True,
                    "message": "Message received and processed successfully.",
                },
                status=status.HTTP_200_OK,
            )

        serializer = MissingReportSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if (
                request.query_params.get("key") == settings.BOT_API_KEY
                and request.query_params.get("source") == "scrapper"
            ):
                serializer.save(source="scrapper")
            else:
                serializer.save(source="web")
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
        report_id = request.GET.get("id")
        try:
            report = MissingReport.objects.get(id=report_id)
        except MissingReport.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Report not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
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
        report_id = request.GET.get("id")
        try:
            report = MissingReport.objects.get(id=report_id)
        except MissingReport.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Report not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        report.delete()
        return Response(
            {
                "success": True,
                "message": "Missing report deleted successfully.",
            },
            status=status.HTTP_200_NO_CONTENT,
        )
