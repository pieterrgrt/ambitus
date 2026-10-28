from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Invite, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "first_name", "language", "is_staff", "date_joined"]
    search_fields = ["email", "first_name"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Profiel", {"fields": ["first_name", "last_name", "language"]}),
        ("Rechten", {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]}),
        ("Data", {"fields": ["last_login", "date_joined"]}),
    ]
    add_fieldsets = [(None, {"classes": ["wide"], "fields": ["email", "password1", "password2"]})]


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ["note", "created_at", "expires_at", "used_by"]
    readonly_fields = ["token", "used_by", "used_at"]
