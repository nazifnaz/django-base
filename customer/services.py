import logging
import os
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.db.models import Count, Sum
from django_currentuser.middleware import get_current_user

from constants import DEFAULT_COUNTRY_CODE
from customer.models import Customer
from messaging.utils import create_customer_email_notifications
from order.models import Item
from system.models import Account, Country
from system.utils import get_errormessage

logger = logging.getLogger(__name__)

to_dict = lambda f: dict(
    (key, value) for key, value in f.__dict__.items() if not callable(value) and not key.startswith('_'))


def create_customer(data, country_id):
    try:
        email = data['email']
        password = data['password']
        first_name = data['first_name']
        last_name = data['last_name']
        middle_name = data['middle_name']
        contact_no = data['contact_no']
        civil_id = data['civil_id']
        issued_country = data['issued_country']
        issued_date = data['issued_date']
        expiry_date = data['expiry_date']
        contact_no_country = country_id
        active = data['active']
        verified = data['verified']
        gender = data['gender']
        dob = data['dob']
    except Exception as e:
        context = get_errormessage("REQ-104")
        context['error_status'] = True
        return context
    try:
        user = User.objects.create_user(username=email, password=password, email=email)
    except Exception as e:
        context = {
            "error_status": True,
            'error_en': 'Username Already Exists',
            'error_ar': 'اسم المستخدم موجود بالفعل',
            'exception_message': str(e)
        }
        return context
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    customer = Customer(
        email=email,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        contact_no=contact_no,
        civil_id=civil_id,
        issued_country_id=issued_country,
        expiry_date=expiry_date,
        issued_date=issued_date,
        contact_no_country_id=contact_no_country,
        active=active,
        verified=verified,
        gender=gender,
        dob=dob,
        user=user
    )
    customer.save()
    context = {
        'customer_id': customer.id,
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'middle_name': customer.middle_name,
        'gender': customer.gender,
        'dob': customer.dob,
        'contact_no': customer.contact_no,
        'civil_id': customer.civil_id,
        'issued_country_id': customer.issued_country_id,
        'issued_date': customer.issued_date,
        'expiry_date': customer.expiry_date,
        'password': password
    }
    return customer, context


def get_total_amount(qs):
    return qs.aggregate(total_amount=Sum('total'))['total_amount'] or 0


def send_customer_notification_email(customer, context, template=None):
    context.pop('user', None)
    create_customer_email_notifications(template_id=template,
                                        customer=customer, data=context, recipient=customer.email)


def recalculate(cart):
    cart.total = 0
    cart.weight = 0
    for item in cart.items.all():
        cart.total += (item.unit_price * item.quantity)
        cart.weight += (item.quantity * Decimal(item.weight))
    cart.save()


def add_item(product, quantity, cart):
    try:
        item = Item.objects.get(
            cart=cart,
            product_id=product['product_id'],
        )
    except Item.DoesNotExist:
        item = Item(**product)
        item.contract = cart
        item.quantity = quantity
        item.save()
        recalculate(cart)

    else:  # ItemAlreadyExists
        item.quantity = int(quantity)
        item.save()
        recalculate(cart)
    return to_dict(item)


def remove_item(product_id, cart):
    try:
        item = Item.objects.get(contract=cart, product_id=product_id)
    except:
        return "fail"
    else:
        item.delete()
        recalculate(cart)
    return product_id


def get_user_permissions(current_user=None):
    if not current_user:
        current_user = get_current_user()
    groups = list(current_user.groups.values_list('id', flat=True))
    permissions = list(Permission.objects.filter(group__in=groups).distinct().values_list('codename', flat=True))
    return permissions


def get_country(country_code=None):
    if country_code:
        try:
            country = Country.objects.get(code=country_code)
        except Country.DoesNotExist:
            logger.error("Country does not exist")
    if not country:
        country = Country.objects.get(code=DEFAULT_COUNTRY_CODE)
    return country


def calculate_vat(amount, percent=5):
    return round(amount * percent / 100, 2)


def calculate_subtotal(cart):
    subtotal = 0
    for item in cart.items.all():
        subtotal += item.unit_price * item.quantity
    return subtotal


def calculate(cart):
    logger.info("calculate functions is loading")
    cart.total = calculate_subtotal(cart) - cart.discount
    cart.save()
    return cart


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL  # Typically /static/
    sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL  # Typically /static/media/
    mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def get_account(user):
    return Account.objects.filter(accountstaff__user=user).last()


def is_account(user):
    if hasattr(user, 'accountstaff'):
        return True
    return False


def get_cart_count_by_status(qs):
    status_count = qs.values('cart_status_id').annotate(total=Count('cart_status_id')).order_by('total')
    return {i['cart_status_id']: i['total'] for i in status_count}
