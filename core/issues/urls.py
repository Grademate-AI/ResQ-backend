from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.issues.views import IssueViewSet, ProofOfHelpViewSet

router = DefaultRouter(trailing_slash=False)
router.register("issues", IssueViewSet, basename="issues")
router.register("proofs", ProofOfHelpViewSet, basename="proofs")

urlpatterns = router.urls
