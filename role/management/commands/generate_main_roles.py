from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from role.models import CustomPermission, Role
from role.services import get_permission_list, unique_id


class Command(BaseCommand):
    help = 'Generates main roles for different user types.'

    def handle(self, **kwargs):
        role_names = ['Admin', 'Staff', 'App User']
        permissions = CustomPermission.objects.values('user_type', 'codename').order_by('user_type')
        user_type_permissions = {}
        for i in permissions:
            if i['user_type'] in user_type_permissions:
                user_type_permissions[i['user_type']].append(i['codename'])
            else:
                user_type_permissions[i['user_type']] = [i['codename']]
        try:
            role_id = 1  # for pk
            for key, val in user_type_permissions.items():
                for role_name in role_names:
                    print('Creating role %s' % role_name)
                    if role_name == 'App User':
                        if key == 3:  # Check if app user type
                            val = []
                        else:
                            continue
                    if key == 1 and role_name != 'Admin':  # restrict other roles for super admin
                        continue
                    print('Creating roles for user type %s' % key)
                    unique_name_for_group = f"{role_name}_{key}_{unique_id()}"
                    group = Group()
                    group.name = unique_name_for_group
                    group.save()
                    permission_list = get_permission_list(val)
                    print(permission_list)
                    group.permissions.add(*permission_list)
                    role = Role()
                    role.id = role_id
                    role.name = role_name
                    role.group = group
                    role.user_type_id = key
                    role.description = role_name + ' role'
                    role.save()
                    role_id += 1
        except Exception as e:
            print('Cannot create role %s' % e)
