from datetime import datetime
from messaging.models import Notification

from settings.celery import app

import logging
logger = logging.getLogger(__name__)


@app.task
def send_notification(notification_id):
    notification = Notification.objects.get(id=notification_id)
    print(f"Executing Send Notification Script on {datetime.now()}")
    # notification.update(status=Notification.Statuses.INITIATED)
    try:
        notification.send_notification()
        print(f"Execution Complete")
        print(f"Exiting Send Notification Script on {datetime.now()}")
    except:
        notification = "fail"
        # notification.update(status=Notification.Statuses.FAILED)
