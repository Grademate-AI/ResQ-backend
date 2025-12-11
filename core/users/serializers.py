from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from core.users.models import User
from core.utils import enums


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", 
            "first_name", 
            "last_name", 
            "username"
            "email", 
            "account_type", 
            "wallet_address"
        ]


class UserSerializer:

    class Retrieve(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = "__all__"

    class Create(serializers.ModelSerializer):
        password2 = serializers.CharField(
            write_only=True,
            required=True,
            style={"input_type": "password"},
            help_text=_("Confirm Password"),
        )

        class Meta:
            model = User
            fields = [
                "email",
                "first_name",
                "last_name",
                "username"
                "account_type",
                "wallet_address",
                "password",
                "password2",
            ]

        def validate_account_type(self, value):
            if value not in enums.UserAccountType.choices():
                raise serializers.ValidationError("Invalid account type")
            return value

        def validate(self, attrs):
            password = attrs.get("password")
            password2 = attrs.pop("password2", None)
            if password and password2 and password != password2:
                raise serializers.ValidationError({"password": _("Passwords do not match.")})
            return attrs

        def create(self, validated_data):
            validated_data["password"] = make_password(validated_data["password"])
            return super().create(validated_data)

    class Update(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["first_name", "last_name", "wallet_address", "is_verified"]


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class AuthSerializer:
    class Login(serializers.Serializer):
        email = serializers.EmailField(required=True)
        password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class AccountRetrieve(serializers.Serializer):
        user = UserSerializer.Retrieve()
        token = TokenSerializer()

    class TokenRefresh(serializers.Serializer):
        refresh = serializers.CharField()

    class Logout(serializers.Serializer):
        refresh = serializers.CharField()

