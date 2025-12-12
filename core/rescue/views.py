from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from core.rescue.models import RescueStation
from core.rescue.serializers import RescueStationSerializer
from core.utils import exceptions, enums, permissions


@extend_schema(tags=["RescueStations"])
class RescueStationViewSet(viewsets.ModelViewSet):
    queryset = RescueStation.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create"]:
            return RescueStationSerializer.StationCreate
        if self.action in ["update", "partial_update"]:
            return RescueStationSerializer.StationUpdate
        return RescueStationSerializer.StationRetrieve

    def get_permissions(self):
        if self.action == "create":
            return super().get_permissions() + [
                permissions.IsAccountType.IsOrganizationAccount()
            ]
        if self.action in ["update", "partial_update", "destroy"]:
            return super().get_permissions() + [
                permissions.StationPermissions.IsStationOwner()
            ]
        
        return super().get_permissions()

    @extend_schema(request=None, responses={200: RescueStationSerializer.StationRetrieve})
    @action(detail=True, methods=["post"], url_path="join")
    def join(self, request, pk=None):
        station = self.get_object()
        station.members.add(request.user)
        station.save(update_fields=["date_last_modified"])
        data = RescueStationSerializer.StationRetrieve(station).data
        return response.Response(data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["post"], url_path="leave")
    def leave(self, request, pk=None):
        station = self.get_object()
        station.members.remove(request.user)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
