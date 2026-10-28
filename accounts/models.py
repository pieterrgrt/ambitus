import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("An email address is required")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """Logs in with an email address; there is no separate username."""

    username = None
    email = models.EmailField(_("e-mailadres"), unique=True)
    language = models.CharField(
        _("taal"), max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.first_name or self.email


def _invite_token():
    return secrets.token_urlsafe(24)


def _invite_expiry():
    return timezone.now() + timedelta(days=settings.AMBITUS_INVITE_DAYS)


class Invite(models.Model):
    """A single-use link that lets one person create an account."""

    token = models.CharField(max_length=64, unique=True, default=_invite_token, editable=False)
    note = models.CharField(_("voor wie"), max_length=120, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="invites_sent"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=_invite_expiry)
    used_by = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="invite"
    )
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.note or self.token[:8]

    @property
    def is_usable(self):
        return self.used_at is None and self.expires_at > timezone.now()

    def get_absolute_url(self):
        return reverse("signup", args=[self.token])
