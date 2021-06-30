from rest_framework import serializers

from customer.api.serializers import CustomerListSerializer
from customer.models import Customer
from order.models import Cart, Item
from system.api.serializer import CartStatusModeSerializer, PaymentStatusModeSerializer, AccountListSerializer, \
    CountrySerializer
from system.models import CartStatus, PaymentStatus, Country


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('id', 'cart', 'quantity', 'product_id', 'product_name', 'unit_price', 'currency_id',
                  'product_type', 'image_url', 'description')


class CartListSerializer(serializers.ModelSerializer):
    customer = CustomerListSerializer(read_only=True)
    contract_status = CartStatusModeSerializer(read_only=True)
    payment_status = PaymentStatusModeSerializer(read_only=True)
    account = AccountListSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "reference", "cart_status", "payment_status", "total", "order_date",
                  "account", "created", "customer")


class CartSerializer(serializers.ModelSerializer):
    customer = CustomerListSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), source="customer",
                                                     write_only=True,
                                                     required=True)

    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), source="country",
                                                    write_only=True,
                                                    required=False, allow_empty=True, allow_null=True)
    payment_status = PaymentStatusModeSerializer(read_only=True)
    payment_status_id = serializers.PrimaryKeyRelatedField(queryset=PaymentStatus.objects.all(),
                                                           source="payment_status", write_only=True,
                                                           required=False, allow_empty=True, allow_null=True)

    cart_status = CartStatusModeSerializer(read_only=True)
    cart_status_id = serializers.PrimaryKeyRelatedField(queryset=CartStatus.objects.all(),
                                                        source="contract_status",
                                                        write_only=True,
                                                        required=False, allow_empty=True, allow_null=True)

    items = serializers.SerializerMethodField()
    sub_total = serializers.SerializerMethodField()
    reference = serializers.CharField(required=False)

    class Meta:
        model = Cart
        fields = '__all__'

    def get_items(self, obj):
        items = Item.objects.filter(contract_id=obj.id)
        data = ItemSerializer(items, many=True).data
        return data

    def get_sub_total(self, obj):
        subtotal = 0
        for item in obj.items.all():
            subtotal += item.unit_price * item.quantity
        return subtotal
