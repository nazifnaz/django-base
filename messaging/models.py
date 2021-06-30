from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from fcm_django.models import FCMDevice

from customer.models import Customer
from system.models import BaseModel, BaseModelBeforeHistory, Configuration
from .services import SMS, Email, INTERNATIONAL_SMS, SendGridHandler

import logging
logger = logging.getLogger(__name__)


class NotificationTemplate(BaseModelBeforeHistory):
    class Types(models.TextChoices):
        PUSH = "PUSH", "Push"
        EMAIL = "EMAIL", "Email"
        SMS = "SMS", "SMS"

    title = models.CharField(max_length=500)
    body = models.TextField()
    template_type = models.CharField(max_length=255, choices=Types.choices, default=Types.EMAIL)

    def __str__(self):
        return f"{self.title}"


class NotificationConfiguration(BaseModelBeforeHistory):
    Types = (
        (1, "ORDER_CREATE"),
        (2, "CUSTOMER_PICKUP_REQUEST"),
        (3, "CUSTOMER_NOTIFY_DELIVERY")
    )

    event_type = models.PositiveIntegerField(choices=Types, null=True)
    recipient = models.CharField(max_length=255, null=True, blank=True)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.get_event_type_display()}"


class Notification(BaseModelBeforeHistory):
    class Types(models.TextChoices):
        PUSH = "PUSH", "Push"
        EMAIL = "EMAIL", "Email"
        SMS = "SMS", "SMS"
        INTERNATIONAL_SMS = "INTERNATIONAL_SMS", "INTERNATIONAL_SMS"
        SEND_GRID = "SEND_GRID", "SEND_GRID"

    class Statuses(models.TextChoices):
        PENDING = "PENDING", "Pending"
        INITIATED = "INITIATED", "Initiated"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    notification_type = models.CharField(max_length=255, choices=Types.choices, default=Types.PUSH)
    title = models.CharField(max_length=100)
    rendered_message = models.TextField(null=True)
    when = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Statuses.choices, null=True, default=Statuses.PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(null=True, default=0)
    exception = models.TextField(null=True, blank=True)
    recipient = models.TextField(null=True, blank=True)

    # FK Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-when']

    def send_notification(self):
        try:
            if self.customer:
                if self.notification_type == self.Types.PUSH:
                    self.push_notification()
                elif self.notification_type == self.Types.SMS:
                    try:
                        if self.customer.contact_no_country.code == "KW":
                            self.send_sms()
                        else:
                            self.send_international_sms()
                    except:
                        self.send_international_sms()

                elif self.notification_type == self.Types.SMS:
                    self.send_sms()
                elif self.notification_type == self.Types.INTERNATIONAL_SMS:
                    self.send_international_sms()
                elif self.notification_type == self.Types.EMAIL:
                    try:
                        conf = Configuration.objects.last()
                        if conf.email_type == 3: # sendgrid
                            self.send_grid()
                        else:
                            self.send_email()
                    except Exception as e:
                        logger.error("Error sending email, trying default %s"%e)
                        self.send_email()
                elif self.notification_type == self.Types.SEND_GRID:
                    self.send_grid()

            else:
                if self.notification_type == self.Types.SMS:
                    self.send_sms()
                elif self.notification_type == self.Types.INTERNATIONAL_SMS:
                    self.send_international_sms()

                elif self.notification_type == self.Types.EMAIL:
                    self.send_email()

                elif self.notification_type == self.Types.SEND_GRID:
                    self.send_grid()

            self.status = self.Statuses.SENT  # SENT=3
            self.sent_at = timezone.now()

        except Exception as e:
            self.exception = e.args[0]
            self.status = self.Statuses.FAILED  # FAILED=4
        self.save()

    def push_notification(self):
        try:
            devices = FCMDevice.objects.filter(user_id=self.user.id, active=True)
            res = devices.send_message(
                title=self.title,
                body=self.rendered_message
            )
            logger.info("push notification result %s" %res)
            return res

        except Exception as e:
            raise Exception(e.args[0])

    def send_sms(self):
        try:
            response = SMS().send_notification(phone=self.recipient, message=self.rendered_message)
            return response
        except Exception as e:
            raise Exception(e.args[0])

    def send_email(self):
        try:
            response = Email().send_notification(to_email=self.recipient, subject=self.title, message=self.rendered_message)
            return response
        except Exception as e:
            raise Exception(e.args[0])

    def send_grid(self):
        try:
            response = SendGridHandler().send_notification(to_email=self.recipient, subject=self.title, message=self.rendered_message)
            return response
        except Exception as e:
            raise Exception(e.args[0])

    def send_international_sms(self):
        try:

            response = INTERNATIONAL_SMS().send_notification(phone=self.recipient, message=self.rendered_message)
            return response
        except Exception as e:
            raise Exception(e.args[0])
