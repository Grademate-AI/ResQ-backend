from django.shortcuts import get_object_or_404
from rest_framework import response, status, viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action

from core.issues.models import Issue
from core.issues.serializers import IssueSerializer
# from core.rewards.services import RewardEngine
from core.utils import enums, exceptions
from core.utils import permissions


@extend_schema(tags=["Issues"])
class IssueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):

        if self.action == "create":
            return super().get_permissions() + [
                permissions.IsAccountType.IsVolunteerAccount()
            ]
        if self.action in ["update", "partial_update"]:
            return super().get_permissions() + [
                permissions.IsObjOwner()
            ]
        
        return super().get_permissions()

    def get_queryset(self, request):
        if request.user.account_type != enums.UserAccountType.VOLUNTEER.value:
            raise exceptions.CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Only volunteer users can access issues list",
            )

        resolved = request.query_params.get("resolved")
        if resolved:
            return Issue.objects.filter(assigned_volunteer=request.user)
        return Issue.objects.filter(user=request.user)

 
    @extend_schema(
        description="Create a new issue.",
        request=IssueSerializer.IssueCreate,
        responses={201: IssueSerializer.IssueRetrieve},
    )
    def create(self, request):
        serializer = IssueSerializer.IssueCreate(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        issue = serializer.save()
        payload = IssueSerializer.IssueRetrieve(issue).data
        return response.Response(payload, status=status.HTTP_201_CREATED)



