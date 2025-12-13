from django.shortcuts import get_object_or_404
from rest_framework import response, status, viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action

from core.issues.models import Issue, ProofOfHelp
from core.issues.serializers import IssueSerializer, ProofOfHelpSerializer
from core.utils import enums, exceptions
from core.utils import permissions
from django.utils import timezone



@extend_schema(tags=["Issues"])
class IssueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):

        if self.action in ["create", "volunteer"]:
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

    @extend_schema(description="Volunteer accepts an issue to work on.", request=None, responses={200: IssueSerializer.IssueRetrieve})
    @action(detail=True, methods=["post"])
    def volunteer(self, request, pk=None):
        issue = self.get_object()
        if issue.status not in [enums.IssueStatus.OPEN.value, enums.IssueStatus.ASSIGNED.value]:
            raise exceptions.CustomException(
                "Issue is not available for acceptance", 
                status.HTTP_400_BAD_REQUEST
            )
        if issue.assigned_volunteer and issue.assigned_volunteer != request.user:
            raise exceptions.CustomException("Issue is assigned to another volunteer", status.HTTP_400_BAD_REQUEST)
        issue.assigned_volunteer = request.user
        issue.status = enums.IssueStatus.ASSIGNED.value
        issue.save(update_fields=["assigned_volunteer", "status", "date_last_modified"])
        return response.Response(IssueSerializer.IssueRetrieve(issue).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Proofs"])
class ProofOfHelpViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create"]:
            return ProofOfHelpSerializer.ProofCreate
        return ProofOfHelpSerializer.ProofRetrieve

    def get_queryset(self):
        user = self.request.user
        qs = ProofOfHelp.objects.all()
        if user.account_type == enums.UserAccountType.VOLUNTEER.value:
            return qs.filter(volunteer=user)
        station_id = self.request.query_params.get("station")
        if station_id:
            return qs.filter(issue__station_id=station_id)
        return qs.none()

    @extend_schema(
        description="Moderator/Owner verifies a proof and triggers on-chain record.", 
        request=None, 
        responses={200: ProofOfHelpSerializer.ProofRetrieve}
    )
    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        proof = get_object_or_404(ProofOfHelp, id=pk)
        issue = proof.issue
        station = issue.station
        # Only station owner can verify for now
        if not station or station.organization.owner_id != request.user.id:
            raise exceptions.CustomException(status_code=403, message="Not permitted to verify proof")
        # Trigger blockchain record (stubbed)
        from core.utils.services.blockchain import ProofOfHelpContract
        points = proof.points or (issue.metadata.get("ai", {}).get("points") if isinstance(issue.metadata, dict) else None) or 0
        client = ProofOfHelpContract()
        volunteer_wallet = getattr(proof.volunteer, "wallet_address", None) or ""
        tx_hash = client.record_help(issue_id=issue.id, volunteer_address=volunteer_wallet, station_id=station.id, proof_hash=proof.proof_hash, points=int(points))
        proof.status = enums.ProofOfHelpStatus.APPROVED.value
        proof.verified_at = timezone.now()
        proof.tx_hash = tx_hash
        proof.save(update_fields=["status", "verified_by", "verified_at", "tx_hash", "date_last_modified"])
        return response.Response(ProofOfHelpSerializer.ProofRetrieve(proof).data, status=status.HTTP_200_OK)



