from django.core.management.base import BaseCommand
from ...models import Settings

class Command(BaseCommand):
    help = 'Updates application settings'

    def handle(self, *args, **options):
        settings, created = Settings.objects.get_or_create(id=1)
        settings.new_relic_license_key = input("Enter New Relic license key: ")
        settings.google_analytics_id = input("Enter Google Analytics ID: ")
        settings.save()
        self.stdout.write(self.style.SUCCESS('Settings updated successfully'))