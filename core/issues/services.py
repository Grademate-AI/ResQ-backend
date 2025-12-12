import json
from typing import Any, Dict, Optional

import requests
from django.conf import settings

from core.utils import exceptions


class BaseAIService:
    """
    Lightweight base service for calling external AI endpoints.
    Mirrors an HTTP client pattern: prepare payload, call, validate, and return.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 15):
        self.base_url = base_url or getattr(settings, "AI_CLASSIFIER_URL", "https://ai-model-vl3b.onrender.com")
        self.api_key = api_key or getattr(settings, "AI_CLASSIFIER_API_KEY", None)
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            resp = requests.post(url, headers=self._headers(), data=json.dumps(payload), timeout=self.timeout)
        except requests.RequestException as e:
            raise exceptions.CustomException(message=f"AI service unreachable: {e}", status_code=503)

        if resp.status_code >= 400:
            # Attempt to extract error message from body
            try:
                data = resp.json()
                msg = data.get("error") or data.get("message") or "AI service error"
            except Exception:
                msg = resp.text or "AI service error"
            raise exceptions.CustomException(message=msg, status_code=resp.status_code)

        try:
            return resp.json()
        except Exception:
            raise exceptions.CustomException(message="Invalid AI response format", status_code=502)


class AIUrgencyClassifierService(BaseAIService):
    """
    Integrates with the AI classifier endpoint to determine issue urgency.

    Expected endpoint: POST /predict
    Example request (adjust based on provider docs):
        {
          "title": "string",
          "description": "string",
          "location": "string",
          "context": { ... optional extra fields ... }
        }

    Example response:
        {
          "label": "HIGH" | "MEDIUM" | "LOW",
          "score": 0.92,
          "meta": { ... }
        }
    """

    def classify(self, *, title: str, description: str, location: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "title": title,
            "description": description,
        }
        if location:
            payload["location"] = location
        if context:
            payload["context"] = context

        result = self._post("/predict", payload)

        # Basic validation of expected fields; keep flexible per docs
        if "label" not in result:
            # Some models return 'prediction' or 'class'; attempt graceful mapping
            label = result.get("prediction") or result.get("class")
            if label:
                result["label"] = label
            else:
                raise exceptions.CustomException(message="AI response missing 'label' field", status_code=502)

        # Normalize score
        if "score" not in result and "confidence" in result:
            result["score"] = result["confidence"]

        return result


def classify_issue_urgency(title: str, description: str, location: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function for callers to classify urgency without managing service lifecycle."""
    service = AIUrgencyClassifierService()
    return service.classify(title=title, description=description, location=location, context=context)


@dataclass
class ClassificationResult:
    urgency_level: str
    urgency_score: float
    ai_confidence: float
    category: str


