import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, views, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from customer.api.filters import CustomerFilter
from customer.api.serializers import AddressSerializer, CustomerSerializer, CustomerListSerializer
from customer.models import Customer, Address
from customer.services import send_customer_notification_email, get_user_permissions
from messaging.constants import WELCOME_EMAIL_TEMPLATE
from system.mixins import DownloadMixin
from system.models import Account
from system.services import create_user_obj, update_user_obj, get_random_password
from system.user_permissions import IsAccount
from system.utils import get_errormessage


class CustomerViewSet(viewsets.ModelViewSet, DownloadMixin):
    permission_classes = (IsAccount,)
    queryset = Customer.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CustomerFilter
    customer_data_details = {
        "addresses": AddressSerializer,
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        else:
            return CustomerSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        data['password'] = get_random_password()
        created, response = create_user_obj(data)
        if not created:
            return response
        user = response
        data['user'] = user.id
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return self.rollback(user, serializer.errors)
        customer = serializer.save()
        for data_type, data_serializer in self.customer_data_details.items():
            error_response = self.add_customer_data(customer, data, data_type, data_serializer)
            if error_response:
                return error_response
        send_customer_notification_email(customer, data, WELCOME_EMAIL_TEMPLATE)
        return Response(self.get_serializer(customer).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        update_user_error = update_user_obj(instance.user, request.data)
        if update_user_error:
            return Response(update_user_error, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        for data_type, data_serializer in self.customer_data_details.items():
            error_response = self.update_customer_data(customer, request.data, data_type, data_serializer, partial)
            if error_response:
                return error_response
        return Response(self.get_serializer(customer).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def add_customer_data(self, customer, request_data, data_type, serializer_class):
        details = request_data.get(data_type, [])
        if not isinstance(details, list):  # Address might be a single object
            details = [details]
        for detail in details:
            detail.update({'customer': customer.id})
        customer_data = serializer_class(data=details, many=True)
        if customer_data.is_valid():
            customer_data.save()
            return None
        else:
            return self.rollback(customer.user, customer_data.errors)

    def update_customer_data(self, customer, request_data, data_type, serializer_class, partial):
        details = request_data.get(data_type, [])
        if not details:
            return None
        if not isinstance(details, list):  # Address might be a single object.
            details = [details]
        for detail in details:
            detail.update({'customer': customer.id})
            if 'id' not in detail:
                customer_data = serializer_class(data=detail)
            else:
                try:
                    data_instance = serializer_class.Meta.model.objects.get(pk=detail['id'])
                except serializer_class.Meta.model.DoesNotExist:
                    return Response({'error_en': '{} ID {} does not exist'.format(data_type, detail['id']),
                                     'error_ar': "{} المعرّف {} غير موجود".format(data_type, detail['id'])},
                                    status=status.HTTP_400_BAD_REQUEST)
                customer_data = serializer_class(data_instance, data=detail, partial=partial)
            customer_data.is_valid(raise_exception=True)
            customer_data.save()
        return None

    def rollback(self, user, errors):
        user.delete()
        error_message = get_errormessage('REQ-104')
        error_message.update({'error_detail': errors})
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        url_path='search',
        url_name='search',
    )
    def customer_search(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(CustomerViewSet, self).list(request, *args, **kwargs)


class ChangeCustomerStatus(APIView):
    permission_classes = (IsAccount,)

    def post(self, request):
        customer_id = request.data.get('customer_id', None)
        if 'status' in request.data and customer_id:
            customer = Customer.objects.get(pk=customer_id)
        else:
            return Response(get_errormessage('REQ-104'), status=status.HTTP_400_BAD_REQUEST)
        customer.active = request.data['status']
        customer.save()
        return Response(
            {
                "message": "Customer is updated successfully.",
            }
        )


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    authentication_classes = []
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        customer_id = self.request.GET.get('customer_id', '')
        try:
            qs = self.queryset.filter(customer=int(customer_id))
        except ValueError:
            qs = self.queryset
        return qs


#  Staff Login
class StaffLoginView(views.APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            email = data['email']
            password = data['password']
        except Exception as e:
            context = {
                'error_en': 'Please Enter valid Username and Password',
                'error_ar': 'الرجاء إدخال اسم مستخدم وكلمة مرور صالحين',
                'error_filed': str(e)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=email, password=password)

        if user:
            context = {}
            if hasattr(user, 'accountstaff'):
                account = user.accountstaff.account
                account_id = account.id
                if not(account.is_active and user.accountstaff.is_active):
                    context = get_errormessage("CUST-102")
            else:
                context = get_errormessage("FORBIDDEN-100")
            if context:
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            refresh = RefreshToken.for_user(user)
            context = {
                'message': 'Authenticated Successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'account': account_id,
                    'permissions': get_user_permissions(user),
                },
                'access_token': str(refresh.access_token),
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            context = get_errormessage("USER-102")
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class UserPermissionView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response({'permissions': get_user_permissions()})


class UniqueValidationView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        validation_type = request.GET.get('type', None)
        field_name = request.GET.get('field_name', None)
        field_data = request.GET.get('field_data', None)
        object_id = request.GET.get('id', None)
        qs = None
        if field_name == 'email':
            return Response(User.objects.filter(username=field_data).exists())
        if validation_type == 'account':
            if field_name == 'contact_no':
                qs = Account.objects.filter(contact_no=field_data)
        elif validation_type == 'customer':
            if field_name == 'contact_no':
                qs = Customer.objects.filter(contact_no=field_data)
        if qs is not None:
            if object_id:
                qs = qs.exclude(pk=object_id)
            return Response(qs.exists())
        return Response(status=status.HTTP_400_BAD_REQUEST)
