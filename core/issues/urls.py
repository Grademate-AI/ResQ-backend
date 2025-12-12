from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.issues.views import IssueViewSet

router = DefaultRouter()
router.register(r"", IssueViewSet, basename="issues")

urlpatterns = [
    path("", include(router.urls)),
    # Legacy endpoints preserved
    path("", IssueViewSet.as_view({"get": "list", "post": "create"}), name="issues"),
    path("<int:issue_id>/", IssueViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="issue-detail"),
    path("<int:issue_id>/accept/", IssueViewSet.as_view({"post": "accept"}), name="issue-accept"),
    path("<int:issue_id>/resolve/", IssueViewSet.as_view({"post": "resolve"}), name="issue-resolve"),
]

