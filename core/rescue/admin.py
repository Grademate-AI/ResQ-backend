from django.contrib import admin

from core.rescue.models import RescueStation


@admin.register(RescueStation)
class RescueStationAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "organization", "date_added")
    search_fields = ("name", "category", "organization__owner__email")
    list_filter = ("category",)

