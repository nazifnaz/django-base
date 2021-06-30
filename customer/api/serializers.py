from django.contrib.auth.models import User
from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from customer.models import Customer, Address
from system.api.serializer import AreaSerializer, CountrySerializer
from system.models import Area, Country


class CustomerSerializer(ModelSerializer):
    email = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    nationality = CountrySerializer(read_only=True)
    nationality_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(),
                                                        source="nationality", write_only=True,
                                                        required=False, allow_empty=True, allow_null=True)
    addresses = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = '__all__'

    def get_addresses(self, obj):
        return AddressSerializer(obj.addresses.last()).data


class CustomerListSerializer(ModelSerializer):
    email = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()

    nationality = CountrySerializer(read_only=True)

    class Meta:
        model = Customer
        fields = ('id', 'email', 'name', 'contact_no', 'civil_id', 'updated', 'nationality')


class AddressSerializer(serializers.ModelSerializer):
    area = AreaSerializer(read_only=True)
    area_id = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all(), source="area", write_only=True,
                                                 required=False, allow_empty=True, allow_null=True)

    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), source="country", write_only=True,
                                                    required=False, allow_empty=True, allow_null=True)

    class Meta:
        model = Address
        fields = ("id", "name", "apartment_no", "block", "street", "avenue", "building_no", "paaci",
                  "address", "city", "country", "country_id", "area", "area_id",
                  "notes", "default", "customer", "floor"
                  )



class CustomerLoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)

    class Meta:
        model = Customer
        fields = ('email', 'password')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
