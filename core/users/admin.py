from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from core.users.models import User, UserSession


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "username", "wallet_address")}),
        ("Permissions", {"fields": ("account_type", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_added", "date_last_modified")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "account_type", "username"),
            },
        ),
    )

    list_display = ("email", "first_name", "last_name", "account_type", )
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name", "username")


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "is_active", "date_added")
    search_fields = ("user__email", "ip_address")

