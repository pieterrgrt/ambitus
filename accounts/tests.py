from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Invite, User


class InviteSignupTests(TestCase):
    def signup(self, invite, email="sanne@example.com"):
        return self.client.post(
            reverse("signup", args=[invite.token]),
            {
                "first_name": "Sanne",
                "email": email,
                "password": "een-lang-wachtwoord-77",
                "language": "de",
                "privacy": "on",
            },
        )

    def test_invite_creates_account_once(self):
        invite = Invite.objects.create(note="Sanne")
        response = self.signup(invite)
        self.assertRedirects(response, reverse("profile"))
        user = User.objects.get(email="sanne@example.com")
        self.assertEqual(user.language, "de")
        invite.refresh_from_db()
        self.assertEqual(invite.used_by, user)

        self.client.logout()
        response = self.signup(invite, email="other@example.com")
        self.assertEqual(response.status_code, 410)
        self.assertFalse(User.objects.filter(email="other@example.com").exists())

    def test_expired_invite_is_refused(self):
        invite = Invite.objects.create(expires_at=timezone.now() - timedelta(days=1))
        self.assertEqual(self.client.get(reverse("signup", args=[invite.token])).status_code, 410)

    def test_unknown_invite_is_404(self):
        self.assertEqual(self.client.get(reverse("signup", args=["nope"])).status_code, 404)

    def test_privacy_must_be_accepted(self):
        invite = Invite.objects.create()
        response = self.client.post(
            reverse("signup", args=[invite.token]),
            {"first_name": "A", "email": "a@example.com", "password": "een-lang-wachtwoord-77", "language": "nl"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())


class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("pieter@example.com", "een-lang-wachtwoord-77", first_name="Pieter")

    def test_login_with_email(self):
        response = self.client.post(
            reverse("login"), {"username": "pieter@example.com", "password": "een-lang-wachtwoord-77"}
        )
        self.assertRedirects(response, reverse("home"))

    def test_user_language_is_used(self):
        self.user.language = "fr"
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'lang="fr"')

    def test_export_and_delete(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account_export"))
        self.assertEqual(response.json()["account"]["email"], "pieter@example.com")

        self.client.post(reverse("account_delete"), {"confirm": "wrong@example.com"})
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        self.client.post(reverse("account_delete"), {"confirm": "pieter@example.com"})
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_only_staff_can_invite(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("invites")).status_code, 302)
        self.user.is_staff = True
        self.user.save()
        self.client.post(reverse("invites"), {"note": "Koen"})
        self.assertEqual(Invite.objects.get().created_by, self.user)
        self.assertContains(self.client.get(reverse("invites")), "/account/aanmelden/")
