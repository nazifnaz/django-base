from rest_framework.response import Response

from system.models import PaymentStatus, ContractStatus


def get_payment_status(payment_status_id):

    status = PaymentStatus.objects.get(id=payment_status_id)
    return status


def get_contract_status(contract_status_id):
    status = ContractStatus.objects.get(id=contract_status_id)
    return status

