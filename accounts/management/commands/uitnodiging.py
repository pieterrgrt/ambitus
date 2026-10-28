from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.models import Invite


class Command(BaseCommand):
    help = "Maak een uitnodigingslink voor een nieuw account."

    def add_arguments(self, parser):
        parser.add_argument("note", nargs="?", default="", help="Voor wie de uitnodiging is")
        parser.add_argument("--base-url", default=getattr(settings, "AMBITUS_BASE_URL", ""))

    def handle(self, note, base_url, **options):
        invite = Invite.objects.create(note=note)
        self.stdout.write(f"{base_url.rstrip('/')}{invite.get_absolute_url()}")
