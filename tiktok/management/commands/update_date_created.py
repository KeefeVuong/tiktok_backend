# update_date_created.py

from django.core.management.base import BaseCommand
from tiktok.models import WeeklyReport
from datetime import datetime

class Command(BaseCommand):
    help = 'Update date_created field based on the title'

    def handle(self, *args, **options):
        queryset = WeeklyReport.objects.all()
        for instance in queryset:
            if instance.title:
                start_date_str = instance.title.split(' -- ')[0]
                start_date = datetime.strptime(start_date_str, '%d/%m/%y').date()
                instance.created_date = start_date
                instance.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated date_created field for existing instances'))
