from django.contrib import admin
from django.db.models import Sum

from .models import AIUsage, Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    # Only metadata: the content belongs to the user.
    list_display = ["user", "status", "created_at"]
    list_filter = ["status"]
    fields = ["user", "status", "created_at"]
    readonly_fields = fields


@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "action", "model", "input_tokens", "output_tokens", "ok"]
    list_filter = ["action", "ok", "model"]
    date_hierarchy = "created_at"

    def changelist_view(self, request, extra_context=None):
        totals = self.get_queryset(request).aggregate(i=Sum("input_tokens"), o=Sum("output_tokens"))
        extra_context = {**(extra_context or {}), "title": f"AI-gebruik (totaal: {totals['i'] or 0} in, {totals['o'] or 0} uit)"}
        return super().changelist_view(request, extra_context)
