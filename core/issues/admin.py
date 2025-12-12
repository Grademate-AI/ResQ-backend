from django.contrib import admin

from core.issues.models import Issue


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ( 
        "user", 
        "urgency_level",
        "ai_confidence", 
        "status", 
        "assigned_volunteer", 
        "date_added"
    )
    list_filter = ("urgency_level", "ai_confidence", "status", "category")
    search_fields = ("description", "user__email")


