from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.issues.views import IssueViewSet

router = DefaultRouter(trailing_slash=False)
router.register("issues", IssueViewSet, basename="issues")

urlpatterns = router.urls
