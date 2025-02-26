from django.core.management.base import BaseCommand
from tradeapp.models import Offer

class Command(BaseCommand):
    help = 'Deletes all entries from the Offer table'

    def handle(self, *args, **kwargs):
        Offer.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all offers'))