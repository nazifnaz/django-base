from django.contrib.auth.models import Group
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from role.api.serializers import RoleSerializer, CustomPermissionSerializer, RoleListSerializer
from role.models import Role, CustomPermission
from role.services import unique_id, get_permission_list


class RoleViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Role.objects.all()
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return RoleListSerializer
        else:
            return RoleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        custom_permission = self.request.data.get('permissions', [])
        applied_permission = get_permission_list(custom_permission)
        user_type = self.request.data.get('user_type', None)
        try:
            unique_name_for_group = f"{request.data.get('name')}_{user_type}_{unique_id()}"
            group = Group()
            group.name = unique_name_for_group
            group.save()
            group.permissions.add(*applied_permission)

            data = request.data
            data['group'] = group.id
            data['user_type'] = user_type
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        except Exception as e:
            return Response({"error_en": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        custom_permission = self.request.data.get('permissions', [])
        applied_permission = get_permission_list(custom_permission)
        group = self.get_object().group
        group.permissions.clear()
        group.permissions.add(*applied_permission)
        return Response(serializer.data)


class CustomPermissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CustomPermissionSerializer
    permission_classes = (IsAuthenticated,)
    queryset = CustomPermission.objects.all()
    pagination_class = None

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        serialized_data = serializer.data
        data = {}
        for item in serialized_data:
            if not item['model_name'] in data:
                data[item['model_name']] = {
                    'model_name_en': item['model_name_en'],
                    'model_name_ar': item['model_name_ar'],
                    'permissions': [self.get_permission_data(item)]
                }
            else:
                data[item['model_name']]['permissions'].append(self.get_permission_data(item))
        return Response(data.values())

    def get_permission_data(self, item):
        return {
            'id': item['id'],
            'name_en': item['name_en'],
            'name_ar': item['name_ar'],
            'codename': item['codename']
        }
