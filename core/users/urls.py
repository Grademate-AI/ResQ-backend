from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.users.views import UserViewSet, AuthViewSet, OrganizationViewSet

router = DefaultRouter(trailing_slash=False)


router.register("users", UserViewSet, basename="users")
router.register("auth", AuthViewSet, basename="auth")
router.register("organizations", OrganizationViewSet, basename="organizations")

urlpatterns = router.urls

