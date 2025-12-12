from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils import enums, mixins


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
        self, email: str, first_name: str, last_name: str, password: str, **extra_fields
    ):
        if not email:
            raise ValueError("The email field is required")
        if not first_name:
            raise ValueError("The first name field is required")
        if not last_name:
            raise ValueError("The last name field is required")
        
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            first_name=first_name, 
            last_name=last_name, 
            **extra_fields
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(
            self, email: str, first_name: str, last_name: str, password: str = None, **extra_fields
        ):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, first_name, last_name, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        first_name: str, 
        last_name: str, 
        password: str,
        account_type: str = enums.UserAccountType.SUPER_ADMIN.value,
        **extra_fields,
    ):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        assert (
            account_type == enums.UserAccountType.SUPER_ADMIN.value
            and account_type in enums.UserAccountType.values()
        )
        extra_fields.setdefault("account_type", account_type)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, first_name, last_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, mixins.BaseModelMixin):
    first_name = models.CharField(
        _("First Name"), max_length=255, null=False, blank=False
    )
    last_name = models.CharField(
        _("Last Name"), max_length=255, null=False, blank=False
    )
    email = models.EmailField(
        _("Email address"), unique=True
    )
    username = models.CharField(
        _("Username"), null=True, blank=True, max_length=50, unique=True
    )
    account_type = models.CharField(
        _("Account Type"),
        max_length=20,
        choices=enums.UserAccountType.choices(),
        default=enums.UserAccountType.SUPER_ADMIN.value,
    )
    wallet_address = models.CharField(
        _("Wallet Address"), max_length=255, null=True, blank=True
    )
    is_verified = models.BooleanField(_("Identity Verified"), default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.email} ({self.role})"

    def retrieve_auth_token(self) -> dict:
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class UserSession(mixins.BaseModelMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    refresh = models.CharField(max_length=255, unique=True, null=True, blank=True)
    access = models.CharField(max_length=255, unique=True, null=True, blank=True)
    ip_address = models.CharField(max_length=255, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("User Session")
        verbose_name_plural = _("User Sessions")

    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"


class Organization(mixins.BaseModelMixin):
    name = models.CharField(max_length=255)
    org_type = models.CharField(
        _("Organization Type"),
        max_length=50,
        choices=enums.OrganizationType.choices(),
        default=enums.OrganizationType.OTHER.value
    )
    issue_interests = models.JSONField(default=list, blank=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owned_organization')

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    def __str__(self):
        return f"{self.name} ({self.org_type})"

