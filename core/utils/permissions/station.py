from rest_framework.permissions import BasePermission
from core.utils import enums



class StationPermissions:
    class IsStationMember(BasePermission):
        """
        Allows access only to members of the rescue station.
        """

        message: str

        def has_permission(self, request, view):
            station_id = view.kwargs.get("pk") or request.data.get("station_id")
            if not station_id:
                self.message = "Station ID is required"
                return False

            is_member = request.user.stations.filter(id=station_id).exists()
            if not is_member:
                self.message = "You are not a member of this rescue station"
            return is_member

    class IsStationOwner(BasePermission):
        """
        Allows access only to the owner organization of the rescue station.
        """

        message: str

    def has_object_permissions(self, request, view, obj):
        self.message = "You do not have permission to access this object."
        return obj.organization.owner == request.user