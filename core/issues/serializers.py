import hashlib, json as pyjson

from rest_framework import serializers
from django.utils import timezone

from core.issues.models import Issue, ProofOfHelp
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
                "station",
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
            data = None
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



class ProofOfHelpSerializer:
    class ProofCreate(serializers.ModelSerializer):
        class Meta:
            model = ProofOfHelp
            fields = ["issue", "proof_media", "notes", "points", "metadata"]

        def validate_issue(self, value: Issue):
            request = self.context.get("request")
            if value.assigned_volunteer_id != request.user.id:
                raise serializers.ValidationError("You are not assigned to this issue")
            return value

        def create(self, validated_data):
            
            request = self.context.get("request")
            validated_data["volunteer"] = request.user
            payload = {
                "proof_media": validated_data.get("proof_media", []),
                "notes": validated_data.get("notes", ""),
                "issue_id": validated_data["issue"].id,
                "volunteer_id": request.user.id,
            }
            proof_hash = hashlib.sha256(pyjson.dumps(payload, sort_keys=True).encode()).hexdigest()
            validated_data["proof_hash"] = proof_hash
            return super().create(validated_data)

    class ProofRetrieve(serializers.ModelSerializer):
        class Meta:
            model = ProofOfHelp
            fields = "__all__"



