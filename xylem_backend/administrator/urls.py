from django.urls import path
from administrator.views import ManageMissingReportsView


urlpatterns = [
    path(
        "missing-reports/",
        ManageMissingReportsView.as_view(),
        name="manage_missing_reports",
    ),
]
