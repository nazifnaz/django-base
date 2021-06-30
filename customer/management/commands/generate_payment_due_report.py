import csv
import datetime
import os

from django.core.management import BaseCommand

from constants import PAYMENT_STATUS
from customer.models import ContractPayment
from messaging.services import Email


class Command(BaseCommand):
    help = 'Generates CSV report for payments due.'

    def add_arguments(self, parser):
        parser.add_argument('--due_date', required=True)
        parser.add_argument('--email', help='To email - to send the generated csv file.')

    def handle(self, due_date, email, **kwargs):
        due_date_time = datetime.datetime.strptime(due_date, '%Y-%m-%d')
        if not email:
            email = 'nazif@shubbaktech.com'
            print("Email not provided. Using the default email: ", email)
        payments = ContractPayment.objects.filter(due_date__lte=due_date_time, payment_status=PAYMENT_STATUS.UNPAID)
        if not payments:
            print('There are no pending payments on ', due_date)
            return 'Exiting'
        filename = 'payment_report_{}.csv'.format(str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')))
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['S No.', 'ID', 'Contract', 'Contract Reference', 'Order Date', 'Due Date', 'Amount', 'Customer'])
            index = 1
            for i in payments:
                csv_writer.writerow([index, i.id, i.contract_id, i.contract.reference, i.contract.order_date,
                                     i.due_date, i.amount, i.contract.customer.name])
                index += 1
        Email().send_notification(
            to_email=email,
            attachments=[filename],
            subject='Payments Due Report CSV',
            message='Please find the attached CSV report for the payments which are due on {}.'.format(due_date)
        )
        print("Email sent to {} successfully.".format(email))
        os.remove(filename)
        print("Removing the file after success.")
