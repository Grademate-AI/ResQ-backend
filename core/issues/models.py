from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.utils import enums, mixins


class Issue(mixins.BaseModelMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="issues",
    )
    description = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=enums.IssueCategory.choices(),
        default=enums.IssueCategory.OTHER.value,
    )
    urgency_level = models.CharField(
        max_length=20,
        choices=enums.UrgencyLevel.choices(),
        default=enums.UrgencyLevel.MEDIUM.value,
    )
    ai_confidence = models.DecimalField(
        _("AI Confidence"), max_digits=5, decimal_places=2, default=0
    )
    location = models.CharField(max_length=255, null=True, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20,
        choices=enums.IssueStatus.choices(),
        default=enums.IssueStatus.OPEN.value,
    )
    assigned_volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues",
    )
    reward_points = models.IntegerField(default=0)
    resolved_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")
        ordering = ("-date_added",)

    def mark_resolved(self):
        self.status = enums.IssueStatus.RESOLVED.value
        self.resolved_at = timezone.now()
        self.save(update_fields=["status", "resolved_at", "date_last_modified"])


