from django.template import Template, Context
from django.utils import timezone

from constants import CHANEL_TYPE
from messaging.models import NotificationTemplate, Notification, NotificationConfiguration
from messaging.services import get_configuration_email_type
from messaging.tasks import send_notification
import logging
logger = logging.getLogger(__name__)


def render_notification_template(template, data):
    template = Template(template)
    return template.render(Context(data))  # dict(obj=post, subscriber=subscriber)))


def create_post_notifications(template_id=None, post=None, users=None):
    notifications = list()
    if template_id and post and users:
        template = NotificationTemplate.objects.get(pk=template_id)
        for user in users:
            title = render_notification_template(getattr(template, f"title_{user.notification_language}"),
                                                 dict(post=post, subscriber=user))
            body = render_notification_template(getattr(template, f"body_{user.notification_language}"),
                                                dict(post=post, subscriber=user))
            notification = Notification(
                notification_type=Notification.Types.EMAIL,
                title=title,
                rendered_message=body,
                when=timezone.now(),
                user=user,
                template=template
            )
            notifications.append(notification)
        Notification.objects.bulk_create(notifications)
    return notifications


def create_user_notifications(template_id=None, customers=None, data=dict(), recipient=None, language=None):
    notifications = list()
    if template_id and customers:
        template = NotificationTemplate.objects.get(pk=template_id)
        for user in customers:
            try:
                title = render_notification_template(getattr(template, f"title_{language}"),
                                                     dict(user=user.customer, **data))
                body = render_notification_template(getattr(template, f"body_{language}"),
                                                    dict(user=user.customer, **data))
            except:
                title = render_notification_template(getattr(template, f"title_en"),
                                                     dict(user=user.customer, **data))
                body = render_notification_template(getattr(template, f"body_en"),
                                                    dict(user=user.customer, **data))

            notification = Notification(
                notification_type=Notification.Types.EMAIL,
                title=title,
                rendered_message=body,
                when=timezone.now(),
                recipient=recipient,
                user=user,
                customer=user.customer,
                template=template
            )
            notification.save()

            task = send_notification.delay(notification.id)
            return notifications


def create_mobile_notifications(template_id=None, user=None, data=dict(), recipient=None, language=None):
    notifications = list()
    if template_id and user.customer:
        template = NotificationTemplate.objects.get(pk=template_id)

        try:
            title = render_notification_template(getattr(template, f"title_{language}"),
                                                 dict(user=user.customer, **data))
            body = render_notification_template(getattr(template, f"body_{language}"),
                                                dict(user=user.customer, **data))
        except:
            title = render_notification_template(getattr(template, f"title_en"),
                                                 dict(user=user.customer, **data))
            body = render_notification_template(getattr(template, f"body_en"),
                                                dict(user=user.customer, **data))

        try:
            if user.customer.contact_no_country.code == "KW":
                type = Notification.Types.SMS
            else:
                type = Notification.Types.INTERNATIONAL_SMS
        except:
            type = Notification.Types.INTERNATIONAL_SMS

        notification = Notification(
            notification_type=type,
            title=title,
            rendered_message=body,
            when=timezone.now(),
            recipient=recipient,
            user=user,
            customer=user.customer,
            template=template
        )
        notification.save()
        task = send_notification.delay(notification.id)

        return notifications


def create_campaign_notifications(template_id=None, customers=None, data=dict(), recipient=None, language=None):
    if template_id:
        template = NotificationTemplate.objects.get(pk=template_id)

        try:
            title = render_notification_template(getattr(template, f"title_{language}"),
                                                 dict(user=None, **data))
            body = render_notification_template(getattr(template, f"body_{language}"),
                                                dict(user=None, **data))
        except:
            title = render_notification_template(getattr(template, f"title_en"),
                                                 dict(user=None, **data))
            body = render_notification_template(getattr(template, f"body_en"),
                                                dict(user=None, **data))

        notification = Notification(
            notification_type=Notification.Types.SEND_GRID,
            title=title,
            rendered_message=body,
            when=timezone.now(),
            recipient=recipient,
            customer=customers,
            template=template
        )
        notification.save()
        return notification


def create_mobile_campaign_notifications(template_id=None, data=dict(), recipient=None, language=None, type=None):

    if template_id :
        template = NotificationTemplate.objects.get(pk=template_id)

        try:
            title = render_notification_template(getattr(template, f"title_{language}"),
                                                 dict(user=None, **data))
            body = render_notification_template(getattr(template, f"body_{language}"),
                                                dict(user=None, **data))
        except:
            title = render_notification_template(getattr(template, f"title_en"),
                                                 dict(user=None, **data))
            body = render_notification_template(getattr(template, f"body_en"),
                                                dict(user=None, **data))

        if type == CHANEL_TYPE.SMS:
            notification_type = Notification.Types.SMS
        else:
            notification_type = Notification.Types.INTERNATIONAL_SMS

        notification = Notification(
            notification_type=notification_type,
            title=title,
            rendered_message=body,
            when=timezone.now(),
            recipient=recipient,
            user=None,
            customer=None,
            template=template
        )
        notification.save()
        return notification


def create_push_campaign_notifications(template_id=None, data=dict(), language=None):
    if template_id:
        template = NotificationTemplate.objects.get(pk=template_id)

        try:
            title = render_notification_template(getattr(template, f"title_{language}"),
                                                 dict(user=None, **data))
            body = render_notification_template(getattr(template, f"body_{language}"),
                                                dict(user=None, **data))
        except:
            title = render_notification_template(getattr(template, f"title_en"),
                                                 dict(user=None, **data))
            body = render_notification_template(getattr(template, f"body_en"),
                                                dict(user=None, **data))

        notification = Notification(
            notification_type=Notification.Types.PUSH,
            title=title,
            rendered_message=body,
            when=timezone.now(),
            recipient=None,
            customer=None,
            template=template
        )
        notification.save()
        return notification


def create_customer_mobile_notifications(template_id=None, customer=None, data=dict(), recipient=None, language=None):
    notifications = list()
    if template_id and customer:
        template = NotificationTemplate.objects.get(pk=template_id)

        try:
            title = render_notification_template(getattr(template, f"title_{language}"),
                                                 dict(user=customer, **data))
            body = render_notification_template(getattr(template, f"body_{language}"),
                                                dict(user=customer, **data))
        except:
            title = render_notification_template(getattr(template, f"title_en"),
                                                 dict(user=customer, **data))
            body = render_notification_template(getattr(template, f"body_en"),
                                                dict(user=customer, **data))

        try:
            if customer.contact_no_country.code == "KW":
                type = Notification.Types.SMS
            else:
                type = Notification.Types.INTERNATIONAL_SMS
        except:
            type = Notification.Types.INTERNATIONAL_SMS

        notification = Notification(
            notification_type=type,
            title=title,
            rendered_message=body,
            when=timezone.now(),
            recipient=recipient,
            user=None,
            customer=customer,
            template=template
        )
        notification.save()

        task = send_notification.delay(notification.id)

        return notifications


def create_customer_email_notifications(template_id=None, customer=None, data=dict(), recipient=None, language=None):
    notifications = list()
    if template_id:
        template = NotificationTemplate.objects.get(pk=template_id)
        try:
            title = render_notification_template(getattr(template, f"title_{language}"),
                                                 dict(user=customer, **data))
            body = render_notification_template(getattr(template, f"body_{language}"),
                                                dict(user=customer, **data))
        except:
            title = render_notification_template(getattr(template, f"title_en"),
                                                 dict(user=customer, **data))
            body = render_notification_template(getattr(template, f"body_en"),
                                                dict(user=customer, **data))

        try:
            channel = get_configuration_email_type()
        except:
            channel= Notification.Types.EMAIL

        notification = Notification(
            notification_type=channel,
            title=title,
            rendered_message=body,
            when=timezone.now(),
            recipient=recipient,
            user=None,
            customer=customer,
            template=template
        )
        notification.save()
        task = send_notification.delay(notification.id)

        return notifications


def create_user_email_notifications(template_id=None, user=None, data=dict(), recipient=None, language=None):
    notifications = list()
    if template_id:
        template = NotificationTemplate.objects.get(pk=template_id)
        try:
            title = render_notification_template(getattr(template, f"title_{language}"),
                                                 dict(user=user, **data))
            body = render_notification_template(getattr(template, f"body_{language}"),
                                                dict(user=user, **data))
        except:
            title = render_notification_template(getattr(template, f"title_en"),
                                                 dict(user=user, **data))
            body = render_notification_template(getattr(template, f"body_en"),
                                                dict(user=user, **data))

        try:
            channel = get_configuration_email_type()
        except:
            channel= Notification.Types.EMAIL

        notification = Notification(
            notification_type=channel,
            title=title,
            rendered_message=body,
            when=timezone.now(),
            recipient=recipient,
            user=user,
            customer=None,
            template=template
        )
        notification.save()
        task = send_notification.delay(notification.id)

        return notifications


def create_customer_push_campaign_notifications(template_id=None, customer=None, data=dict(), language=None):
    if template_id:
        template = NotificationTemplate.objects.get(pk=template_id)
        logger.info("inside the push Templates is loading %s" % template_id)
        try:
            title = render_notification_template(getattr(template, f"title_{language}"),
                                                 dict(user=None, **data))
            body = render_notification_template(getattr(template, f"body_{language}"),
                                                dict(user=None, **data))
        except:
            title = render_notification_template(getattr(template, f"title_en"),
                                                 dict(user=None, **data))
            body = render_notification_template(getattr(template, f"body_en"),
                                                dict(user=None, **data))


        try:
            user = customer.user
        except:
            user = None

        notification = Notification(
            notification_type=Notification.Types.PUSH,
            title=title,
            rendered_message=body,
            when=timezone.now(),
            recipient=None,
            user=user,
            customer=customer,
            template=template
        )
        notification.save()
        task = send_notification.delay(notification.id)
        return notification


def create_user_notifications_all_channel(template_id=None, customer=None, data=dict(), recipient=None, language=None, channel=None):
    if template_id:
        template = NotificationTemplate.objects.get(pk=template_id)
        try:
            title = render_notification_template(getattr(template, f"title_{language}"),
                                                 dict(user=customer, **data))
            body = render_notification_template(getattr(template, f"body_{language}"),
                                                dict(user=customer, **data))
        except:
            title = render_notification_template(getattr(template, f"title_en"),
                                                 dict(user=customer, **data))
            body = render_notification_template(getattr(template, f"body_en"),
                                                dict(user=customer, **data))

        try:
            channel = get_configuration_email_type()
        except:
            channel= channel

        notification = Notification(
            notification_type=channel,
            title=title,
            rendered_message=body,
            when=timezone.now(),
            recipient=recipient,
            user=None,
            customer=customer,
            template=template
        )
        notification.save()
        task = send_notification.delay(notification.id)
        return notification


def send_notification_for_event(event_type,data,customer=None,language=None):
    if 'user' in data:
        data.pop('user')

    configurations = NotificationConfiguration.objects.filter(event_type=event_type)
    for configuration in configurations:
        if configuration.template.template_type == "PUSH":
            create_customer_push_campaign_notifications(template_id=configuration.template.id, customer=customer, data=data, language=language)
        elif configuration.template.template_type == "EMAIL":
            create_customer_email_notifications(template_id=configuration.template.id, customer=customer, data=data,
                                                recipient=customer.email, language=language)
        elif configuration.template.template_type == "SMS":
            create_customer_mobile_notifications(template_id=configuration.template.id, customer=customer, data=data,
                                                 recipient=customer.contact_no, language=language)
