from rest_framework import serializers

from core.rescue.models import RescueStation
from core.users.serializers import BaseUserSerializer, OrganizationSerializer


class RescueStationSerializer:
    class StationRetrieve(serializers.ModelSerializer):
        organization = OrganizationSerializer.OrganizationRetrieve(read_only=True)
        members = BaseUserSerializer(many=True, read_only=True)

        class Meta:
            model = RescueStation
            fields = "__all__"

    class StationCreate(serializers.ModelSerializer):
        class Meta:
            model = RescueStation
            fields = ["name", "category", "description"]

        def create(self, validated_data):
            request = self.context.get("request")
            return RescueStation.objects.create(organization=request.user.owned_organization, **validated_data)

    class StationUpdate(serializers.ModelSerializer):
        class Meta:
            model = RescueStation
            fields = ["name", "category", "description"]

