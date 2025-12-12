from rest_framework.routers import DefaultRouter

from core.rescue.views import RescueStationViewSet

router = DefaultRouter(trailing_slash=False)
router.register("stations", RescueStationViewSet, basename="rescue-stations")

urlpatterns = router.urls
