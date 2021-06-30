from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from messaging.models import *


class Command(BaseCommand):
    help = 'Service for sending Global message.'

    def handle(self, *args, **options):
        if Notification.objects.filter(when__lte=datetime.now(), status=Notification.Statuses.PENDING).exclude(sent_at__isnull=False).exists():
            print(f"Executing Send Notification Script on {datetime.now()}")
            notifications = Notification.objects.filter(when__lte=datetime.now(), status=Notification.Statuses.PENDING).exclude(sent_at__isnull=False)
            print(f"Total Count {notifications.count()}")
            notification_ids = list(notifications.values_list('id', flat=True))
            notifications.update(status=Notification.Statuses.INITIATED)
            for notification in Notification.objects.filter(pk__in=notification_ids):
                notification.send_notification()
            print(f"Execution Complete")
            print(f"Exiting Send Notification Script on {datetime.now()}")
