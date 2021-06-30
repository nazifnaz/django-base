import os


def get_download_path(instance, filename):
    return os.path.join('Downloads', '%s' % instance.created_by, filename)


def get_profile_path(instance, filename):
    return os.path.join('profile', '%s' % instance.user_id, filename)


def get_customer_path(instance, filename):
    return os.path.join('customer_docs', '%s' % instance.customer_id, filename)


def get_account_path(instance, filename):
    return os.path.join('account', '%s' % instance.name, filename)


def get_document_storage_path(instance, filename):
    folder = 'default'
    if hasattr(instance, 'account_id'):
        folder = instance.account_id
    elif hasattr(instance, 'contract_id'):
        folder = instance.contract_id
    elif hasattr(instance, 'customer_id'):
        folder = instance.customer_id
    return os.path.join('%s/%s' % (instance.__class__.__name__, folder), filename)

