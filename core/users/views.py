from django.contrib.auth import authenticate
from rest_framework import response, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action

from core.users.models import User, UserSession
from core.users.serializers import (
    UserSerializer, 
    AuthSerializer, 
    TokenSerializer, 
    OrganizationSerializer
)
from core.users.models import Organization
from core.utils import exceptions
from core.utils import permissions


@extend_schema(tags=["User"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects
    serializer_class = AuthSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsGuestUser()]
        
        return super().get_permissions()

    @extend_schema(
        auth=[],
        description="endpoint to register a new user account",
        request=UserSerializer.Create, 
        responses={201: AuthSerializer.AccountRetrieve}
    )
    def create(self, request):
        serializer = UserSerializer.Create(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()

        auth_token = account.retrieve_auth_token()

        UserSession.objects.create(
            user=account,
            refresh=auth_token["refresh"],
            access=auth_token["access"],
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT"),
            is_active=True,
        )

        data = {
            "user": UserSerializer.Retrieve(instance=account).data, 
            "token": auth_token
        }
        return response.Response(data, status=status.HTTP_201_CREATED)
   
    @extend_schema(
        request=None, 
        responses={200: UserSerializer.Retrieve}
    )
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = UserSerializer.Retrieve(request.user)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserSerializer.Update, 
        responses={200: UserSerializer.Retrieve}
    )
    @action(detail=False, methods=["put", "patch"], url_path="me/update")
    def update_me(self, request):
        serializer = UserSerializer.Update(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        serializer = UserSerializer.Retrieve(instance=user)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class AuthViewSet(viewsets.ViewSet):
    queryset = User.objects
    serializer_class = AuthSerializer

    def get_permissions(self):
        if self.action in ["login", "token_refresh"]:
            return [permissions.IsGuestUser()]
        
        return super().get_permissions()


    @extend_schema(
        auth=[], 
        request=AuthSerializer.Login, 
        responses={200: AuthSerializer.AccountRetrieve}
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = AuthSerializer.Login(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        account = authenticate(request, username=email, password=password)
        if not account:
            raise exceptions.CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid credentials",
            )

        if not account.is_active:
            raise exceptions.CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Authentication failed",
            )

        auth_token = account.retrieve_auth_token()
        UserSession.objects.create(
            user=account,
            refresh=auth_token["refresh"],
            access=auth_token["access"],
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT"),
            is_active=True,
        )
        data = {
            "user": UserSerializer.Retrieve(instance=account).data, 
            "token": auth_token
        }
        return response.Response(data, status=status.HTTP_200_OK)

    
    @extend_schema(
        request=AuthSerializer.Logout, 
        responses={205: None}
    )
    @action(detail=False, methods=["post"])
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                raise exceptions.CustomException("Refresh token is required")
            UserSession.objects.filter(refresh=refresh_token).delete()
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass
        return response.Response(status=status.HTTP_205_RESET_CONTENT)

    
    @extend_schema(
        request=AuthSerializer.TokenRefresh, 
        responses={200: TokenSerializer}
    )
    @action(detail=False, methods=["post"], url_path="token/refresh")
    def token_refresh(self, request):
        serializer = AuthSerializer.TokenRefresh(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]
        try:
            session = UserSession.objects.get(refresh=refresh_token)
            RefreshToken(refresh_token).blacklist()
            token = session.user.retrieve_auth_token()
            session.access = token["access"]
            session.refresh = token["refresh"]
            session.save(update_fields=["access", "refresh", "date_last_modified"])
            return response.Response(token, status=status.HTTP_200_OK)
        except UserSession.DoesNotExist:
            raise exceptions.CustomException(
                message="Session not found. Please login again.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )


@extend_schema(tags=["Organization"])
class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects

    def get_permissions(self):
        if self.action == "create":
            return super().get_permissions() + [
                permissions.IsAccountType.IsOrganizationAccount()
            ]
        if self.action in ["retrieve", "partial_update"]:
            return super().get_permissions() + [
                permissions.IsObjOwner()
            ]
        return super().get_permissions()

    @extend_schema(
        request=OrganizationSerializer.OrganizationCreate,
        responses={201: OrganizationSerializer.OrganizationRetrieve},
    )
    def create(self, request):
        serializer = OrganizationSerializer.OrganizationCreate(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        org = serializer.save()
        return response.Response(OrganizationSerializer.OrganizationRetrieve(org).data, status=status.HTTP_201_CREATED)


