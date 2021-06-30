import logging
import re
import urllib.request
from urllib.parse import quote, unquote

import requests
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from settings import DEFAULT_FROM_EMAIL, SENDGRID_API_KEY, DEFAULT_SENDER_SMS
from system.models import Configuration

logger = logging.getLogger(__name__)


class SMS(object):


    def __init__(self):
        self.url = "http://62.150.26.41/SmsWebService.asmx/send"
        self.url_auth = "http://62.150.26.41/SmsWebService.asmx/authentication"
        self.username = "clouddealz_1"
        self.password = "RmRRsqKn"
        self.token = "BdLvUKCb4VvnRmyMGZvB6QhP"
        self.type = "text"
        self.coding = "unicode"
        self.datetime = "now"
        self.header = {"application/soap+xml; charset=utf-8"},

    def send_notification(self, *args, **kwargs):
        try:
            data = {}
            receiver = kwargs.get('phone', None)
            message = kwargs.get('message', None)


            try:
                configurations = Configuration.objects.last()
                sender_sms = configurations.sender_sms or DEFAULT_SENDER_SMS
            except:
                sender_sms = DEFAULT_SENDER_SMS
            if receiver:
                response_list = list()
                if isinstance(receiver, list):
                    logger.info("Inside the list ")
                    for i in receiver:
                        logger.debug("Sending sms %s" % receiver)
                        data = {
                            "username": self.username,
                            "password": self.password,
                            "token": self.token,
                            "type": self.type,
                            "coding": self.coding,
                            "datetime": self.datetime,
                            "sender": quote(sender_sms),
                            "dst": i
                        }
                        try:
                            data["message"] = strip_tags(message)
                        except:
                            try:
                                data["message"] = re.sub('<[^<]+?>', '', message)
                            except:
                                data["message"] = message

                        logger.debug("Sending sms: %s" % data)
                        response = requests.post(
                            url=self.url,
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            data=data
                        )
                        response_list.append({
                            'receiver': receiver,
                            'response': response
                        })
                else:
                    logger.debug("Sending sms %s" % receiver)
                    data = {
                        "username": self.username,
                        "password": self.password,
                        "token": self.token,
                        "type": self.type,
                        "coding": self.coding,
                        "datetime": self.datetime,
                        "sender": quote(sender_sms),
                        "dst": receiver
                    }
                    try:
                        data["message"] = strip_tags(message)
                    except:
                        try:
                            data["message"] = re.sub('<[^<]+?>', '', message)
                        except:
                            data["message"] = message

                    logger.debug("Sending sms: %s" % data)
                    response = requests.post(
                        url=self.url,
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        data=data
                    )
                    response_list.append({
                        'receiver': receiver,
                        'response': response
                    })
                return response_list

        except Exception as e:
            raise Exception(e.args[0])


class Email(object):

    def send_notification(self, *args, **kwargs):
        try:
            configurations = Configuration.objects.last()
            sender_email = configurations.sender_email or DEFAULT_FROM_EMAIL
        except:
            sender_email = DEFAULT_FROM_EMAIL

        from_email = kwargs.get('from_email', sender_email)
        to_email = kwargs.get('to_email', None)
        subject = kwargs.get('subject', None)
        message = kwargs.get('message', None)
        if from_email and to_email and subject and message:
            try:
                email = EmailMessage(
                    subject,
                    message,
                    from_email,
                    [to_email],
                    bcc=[from_email],
                    reply_to=[from_email],
                )
                email.content_subtype = "html"
                email.send(fail_silently=True)
                return True
            except Exception as e:
                logger.debug("%s" % e.args[0])
        raise Exception("Missing required parameters Unable to send Email")

class INTERNATIONAL_SMS(object):

    def send_notification(self, *args, **kwargs):
        try:
            try:
                configurations = Configuration.objects.last()
                sender_sms = configurations.sender_sms or DEFAULT_SENDER_SMS
            except:
                sender_sms = DEFAULT_SENDER_SMS

            recipients = kwargs.get('phone', None)
            recipients = recipients.split(",")
            chunks = [recipients[x:x + 5] for x in range(0, len(recipients), 5)]
            for i in chunks:
                recipient = ",".join(i)
                message = kwargs.get('message', None)
                URL_TEMPLATE = "http://smsapi.estee.digital/sms/smsapi?api_key=C20018395c111cc8bdfae2.70635832&type=unicode&contacts=" + recipient + "&senderid=" + str(
                    sender_sms) + "&msg=" + quote(strip_tags(message)) + ""
                page = urllib.request.Request(URL_TEMPLATE, headers={'User-Agent': 'Mozilla/5.0'})
                contents = urllib.request.urlopen(page).read()
                logger.debug('Message response:%s' % contents)
            return True
        except Exception as e:
                logger.debug("%s" % e.args[0])
        raise Exception("Missing required parameters Unable to send Message")


def get_configuration_email_type():
    try:
        configurations = Configuration.objects.last()
        type = None
        if configurations.email_type == 1:
            type = "EMAIL"
        if configurations.email_type == 2:
            type = "EMAIL"
        if configurations.email_type == 3:
            type = "SEND_GRID"
        return type
    except:
        return "EMAIL"


class SendGridHandler(object):

    def send_notification(self, *args, **kwargs):
        to_emails = kwargs.get('to_email', None)
        subject = kwargs.get('subject', None)
        message = kwargs.get('message', None)

        try:
            configurations = Configuration.objects.last()
            email_provider = configurations.email_type
            if email_provider and configurations.sendgrid_api_key:
                sendgrid_api_key = configurations.sendgrid_api_key

            else:
                sendgrid_api_key = SENDGRID_API_KEY

            sender_email = configurations.sender_email or DEFAULT_FROM_EMAIL
        except:
            sendgrid_api_key = SENDGRID_API_KEY
            sender_email = DEFAULT_FROM_EMAIL

        sender_name = "Paydo"
        logger.info('Sendgrid mail provider Initiated')

        chunks = [to_emails[x:x + 999] for x in range(0, len(to_emails), 999)]

        for email in chunks:
            message = Mail(
                from_email=(sender_email, sender_name),
                to_emails=email,
                subject=unquote(subject),
                html_content=message,
                is_multiple=True
            )
            # file_path = obj.attachment.path
            # file_type = magic.from_file(file_path, mime=True)
            # filename = os.path.basename(file_path)
            # with open(file_path, 'rb') as f:
            #     data = f.read()
            #     f.close()
            # encoded = base64.b64encode(data).decode()
            # attachment = Attachment()
            # attachment.file_content = FileContent(encoded)
            # attachment.file_type = FileType(file_type)
            # attachment.file_name = FileName(filename)
            # attachment.disposition = Disposition('attachment')
            # attachment.content_id = ContentId('Example Content ID')
            # message.attachment = attachment

            try:
                sg = SendGridAPIClient(sendgrid_api_key)
                response = sg.send(message)

                status_code = response.status_code
                body = response.body
                headers = response.headers

                context = {
                    "status_code": status_code,
                    "body": body,
                    "headers": headers
                }

                logger.info('Sendgrid success data %s' % context)
                logger.info('Sendgrid mail sent successfully')
                return context

            except Exception as e:
                error_message = e
                logger.info('Sendgrid mail sending fail %s' % error_message)
                return error_message


