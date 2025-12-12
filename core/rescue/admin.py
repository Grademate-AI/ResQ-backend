from django.contrib import admin

from core.rescue.models import RescueStation


@admin.register(RescueStation)
class RescueStationAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "ngo", "date_added")
    search_fields = ("name", "category", "ngo__email")
    list_filter = ("category",)

