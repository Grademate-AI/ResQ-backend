from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import mixins
from core.utils import enums
from core.users.models import Organization


class RescueStation(mixins.BaseModelMixin):
    organization = models.OneToOneField(
        to=Organization,
        on_delete=models.CASCADE,
        related_name="stations",
        verbose_name=_("Organization (Owner)"),
    )
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=100,
        choices=enums.IssueCategory.choices(),
    )
    description = models.TextField(blank=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="joined_stations",
        blank=True,
    )
    funding_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )

    class Meta:
        verbose_name = _("Rescue Station")
        verbose_name_plural = _("Rescue Stations")
        ordering = ("-date_added",)

    def __str__(self) -> str:
        return f"{self.name} ({self.category})"

