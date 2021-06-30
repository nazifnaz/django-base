from rest_framework import serializers

from role.models import Role, CustomPermission


class RoleSerializer(serializers.ModelSerializer):

    permission = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_permission(self, obj):
        permissions = obj.group.permissions.values_list('codename', flat=True)
        return permissions


class RoleListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = '__all__'


class CustomPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomPermission
        fields = '__all__'
