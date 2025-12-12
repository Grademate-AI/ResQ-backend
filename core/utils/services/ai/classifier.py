from typing import Any, Dict, Optional, List

from core.utils import exceptions, enums
from core.issues.models import Issue
from core.users.models import User
from .base import BaseAIService


 
class AIUrgencyClassifierService(BaseAIService):
    """
    Integrates with the AI classifier endpoint to determine issue urgency.

    Expected endpoint: POST /predict
        {
        "report_text": string,
        "use_openai": bool,
        "volunteer_score": int,
        "task_complexity": int
        }
    """

    def _normalize_urgency(self, label: str) -> str:
        val = str(label or "").strip().lower()
        if val in {"high", "urgent", "critical"}:
            return enums.UrgencyLevel.HIGH.value
        if val in {"medium", "moderate"}:
            return enums.UrgencyLevel.MEDIUM.value
        return enums.UrgencyLevel.LOW.value

    def _notify_relevant_volunteers(self, urgency_level: str) -> List[str]:
        # Notify volunteers for HIGH urgency
        if urgency_level == enums.UrgencyLevel.HIGH.value:
            volunteers = User.objects.filter(
                account_type=enums.UserAccountType.VOLUNTEER.value, is_active=True
            )
            emails = list(volunteers.values_list("email", flat=True))
            # TODO: Implement actual email sending logic here
            notified = emails
            return notified
 
            # if notified:
            #     meta = issue.metadata or {}
            #     meta["ai_result"]["notified_volunteers"] = notified
            #     issue.metadata = meta
            #     issue.save(update_fields=["metadata", "date_last_modified"])


    def classify(self, data: dict) -> dict:

        result = self.post_json("/predict", data)

        urgency_level = self._normalize_urgency(result.get("urgency"))
        features = result.get("features")
        keywords_score = float(features.get("urgency_keywords_score", 0))
        points = int(result.get("points"))
    
        metadata = {}
        metadata.setdefault("ai_result", {})
        metadata["ai_result"] == features

        data={
            "urgency_level": urgency_level,
            "ai_confidence": keywords_score,
            "metadata": metadata,
            "reward_points": points,
        }
        return data

