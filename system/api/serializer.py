from django.urls import reverse
from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from role.api.serializers import RoleListSerializer
from role.models import Role
from system.models import DocumentType, Account, AccountStaff, Area, Country, \
    PaymentStatus, CartStatus, DownloadJob


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class DocumentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = ('id', 'name', 'name_ar', 'name_en')


class AccountSerializer(ModelSerializer):
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.filter(),
                                                    source="country", write_only=True)

    class Meta:
        model = Account
        fields = '__all__'


class AccountListSerializer(ModelSerializer):

    class Meta:
        model = Account
        fields = '__all__'


class AccountStaffSerializer(serializers.ModelSerializer):
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    account = AccountListSerializer(read_only=True)
    role = RoleListSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(),
                                                 source="role", write_only=True)
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(),
                                                    source="account", write_only=True)

    class Meta:
        model = AccountStaff
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class PaymentStatusModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentStatus
        fields = '__all__'


class CartStatusModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartStatus
        fields = '__all__'


class DownloadJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadJob
        fields = '__all__'
