from rest_framework import serializers
from django.utils import timezone

from core.issues.models import Issue
from core.users.serializers import BaseUserSerializer
from core.utils import enums
from core.utils.services.ai import AIUrgencyClassifierService


class IssueSerializer:
    class IssueRetrieve(serializers.ModelSerializer):
        user = BaseUserSerializer(read_only=True)
        assigned_volunteer = BaseUserSerializer(read_only=True)

        class Meta:
            model = Issue
            fields = "__all__"

    class IssueCreate(serializers.ModelSerializer):
        class Meta:
            model = Issue
            fields = [
                "description",
                "location",
                "attachments",
            ]

        def create(self, validated_data):
            request = self.context.get("request")
            validated_data["user"] = request.user
            description = validated_data["description"]

            payload = {
                "report_text": description,
                "use_openai": True,
                "volunteer_score": 1,
                "task_complexity": 1,
            }
            try:
                service = AIUrgencyClassifierService()
                data = service.classify(data=payload)
            except Exception:
                # Swallow external service errors; issue remains created
                pass

            validated_data.update(data)
            issue = super().create(validated_data)
            return issue

    class IssueUpdate(serializers.ModelSerializer):
        class Meta:
            model = Issue
            fields = ["status", "assigned_volunteer", "attachments", "metadata"]

        def validate_status(self, value):
            if value not in enums.IssueStatus.choices():
                raise serializers.ValidationError("Invalid status")
            return value



