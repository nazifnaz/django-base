from random import random
from time import time

from celery.worker.control import revoke
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response


import random
import string

import logging

from messaging.constants import STAFF_WELCOME_TEMPLATE

logger = logging.getLogger(__name__)


def unique_id(prefix=''):
    return prefix + hex(int(time()))[2:10] + hex(int(time() * 1000000) % 0x100000)[2:7]


def get_random_password():
    letters = string.ascii_letters
    password = ''.join(random.choice(letters) for i in range(10))
    return password


def update_user_role(obj, previous_role=None):
    if obj.role != previous_role:
        obj.user.groups.clear()
        obj.user.groups.add(obj.role.group)
    return


def create_user_obj(data):
    """
    Create user object and return status and response/user object.
    """
    first_name = data.get('first_name', None)
    last_name = data.get('last_name', None)
    email = data.get('email', None)
    password = data.get('password', None)
    if not (email and password):
        return False, Response({"error_en": "Email and Password are mandatory"}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=email).exists():
        return False, Response({"error_en": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    user_data = {"email": email, "password": password, "username": email}
    if last_name:
        user_data["last_name"] = last_name
    if first_name:
        user_data["first_name"] = first_name
    user = User.objects.create_user(**user_data)
    return True, user


def create_staff(user_data, serializer):
    """
    Create staff including the user instance and return Success/Error response.
    """
    data = user_data
    data['password'] = get_random_password()
    created, response = create_user_obj(data)
    if created:
        user = response
        data['user'] = user.id
        serializer = serializer(data=data)
        serializer.is_valid(raise_exception=True)
        staff_obj = serializer.save()
        update_user_role(staff_obj)
        send_staff_notification_email(user, {'email': data['email'], 'password': data['password']},
                                      template=STAFF_WELCOME_TEMPLATE)
        return Response(serializer.data)
    else:
        return response


def update_user_obj(user, data):
    """
    Update user object and return None or Error context.
    """
    updated = False
    if 'first_name' in data:
        updated = True
        user.first_name = data['first_name']
    if 'last_name' in data:
        updated = True
        user.last_name = data['last_name']
    if 'email' in data:
        if User.objects.filter(username=data['email']).exclude(id=user.id).exists():
            return {"error_en": "Email already exists"}
        else:
            updated = True
            user.email = data['email']
            user.username = data['email']
    if updated:
        user.save()
    return None


def update_staff(instance_user, data, serializer):
    """
    Used for updating user instance in Staff and Account Staff.
    serializer is the corresponding serializer.
    """
    serializer.is_valid(raise_exception=True)
    error = update_user_obj(instance_user, data)
    if error:
        return Response(error, status=status.HTTP_400_BAD_REQUEST)
    staff_obj = serializer.save()
    update_user_role(staff_obj)
    return Response(serializer.data)


def cancel_task(task_id):
    revoke(task_id, terminate=True)
    return True


def send_staff_notification_email(user, context, template=None):
    from messaging.utils import create_user_email_notifications
    create_user_email_notifications(template_id=template, user=user, data=context, recipient=user.email)


def is_account(user):
    return hasattr(user, 'accountstaff')


def get_account(user):
    if hasattr(user, 'accountstaff'):
        return user.accountstaff.account
    return None
