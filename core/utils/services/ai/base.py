from typing import Any, Dict, Optional

from django.conf import settings

from core.utils.services.base import BaseService
from core.utils import exceptions
from core.utils.exceptions.handlers import Handlers


class BaseAIService(BaseService):
    """
    Base AI Service built on the shared BaseService.
    Provides helpers for calling the classifier endpoint and parsing responses.
    """

    def __init__(self, base_url: str=None, api_key: str=None):
        super().__init__(
            base_url=base_url or getattr(settings, "AI_URL", "https://ai-model-vl3b.onrender.com"),
            api_key=api_key or getattr(settings, "AI_API_KEY", None),
        )

    def post_json(self, endpoint: str, data: dict, timeout: int = 15) -> dict:
        resp = self.post(endpoint=endpoint, data=data, timeout=timeout)
        Handlers.handle_request_failure(
            resp, f"Failed to reach AI service: {resp.text}"
        )

        try:
            return resp.json()
        except Exception:
            raise exceptions.CustomException(message="Invalid AI response format", status_code=502)