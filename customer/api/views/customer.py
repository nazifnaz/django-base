from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_currentuser.middleware import get_current_user
from rest_framework import views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from customer.api.serializers import CustomerSerializer, CustomerLoginSerializer, UserSerializer
from customer.models import Customer
from customer.services import send_customer_notification_email
from messaging.constants import OTP_NOTIFICATION_TEMPLATE
from messaging.utils import create_mobile_notifications
from system.authentication import CustomJWTAuthentication
from system.user_permissions import IsCustomer
from system.utils import get_errormessage


class CustomerLoginView(views.APIView):
    serializer_class = CustomerLoginSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        reference, contract_id = None, None
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        email = data.get('email', None)
        password = data.get('password', None)
        if not (email and password):
            return Response(get_errormessage('LOGIN-100'), status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=email, password=password)
        if user:
            customer = Customer.objects.filter(user=user).last()
            if not customer:
                context = get_errormessage("CUST-103")
            elif not customer.active:
                context = get_errormessage("CUST-102")
            elif not customer.verified:
                context = get_errormessage("CUST-104")
            else:
                customer_data = UserSerializer(customer.user).data
                customer_data['contact_no'] = customer.contact_no
                refresh = RefreshToken.for_user(user)
                context = {
                    'message': 'Authenticate Successfully',
                    'customer': customer_data,
                    'token': str(refresh.access_token),
                }
                return Response(context, status=status.HTTP_200_OK)
        else:
            context = get_errormessage("USER-102")
        return Response(context, status=status.HTTP_400_BAD_REQUEST)


class CustomerLogoutView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            CustomJWTAuthentication().black_list(request)
            return Response(data={"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(views.APIView):
    model = Customer
    permission_classes = (IsCustomer,)

    def post(self, request, *args, **kwargs):
        current_user = get_current_user()
        username = current_user.username
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        user = authenticate(username=username, password=old_password)
        if user:
            user.set_password(new_password)
            user.save()
            customer = user.customer
            customer_data = CustomerSerializer(customer).data
            refresh = RefreshToken.for_user(user)
            context = {
                'message': 'Password updated successfully',
                'customer': customer_data,
                'token': str(refresh.access_token)
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            context = {
                'error_en': 'old password is wrong',
                'status': status.HTTP_400_BAD_REQUEST
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    permission_classes = [IsCustomer,]
    authentication_classes = []

    def get(self, request):
        phone = request.query_params.get('phone', None)
        if phone:
            try:
                contact_no = (phone[1:] if phone.startswith('0') else phone)
                customer = Customer.objects.filter(contact_no=contact_no).first()
                otp = customer.generate_otp()
            except:
                return Response(get_errormessage("USER-101"), status=status.HTTP_400_BAD_REQUEST)
            data = {"otp": otp}
            try:

                recipient = customer.get_contact_number_with_isd()
                create_mobile_notifications(OTP_NOTIFICATION_TEMPLATE, customer.user, data, recipient, None)
            except:
                return Response({"error_en": "Contact number country should be update"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(get_errormessage("CUST-101"), status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "message": get_errormessage("OTP-101"),
        })

    def post(self, request):
        otp = request.data.get('otp', None)
        phone = request.data.get('phone', None)
        password = request.data.get('password', None)
        if not (otp and phone and password):
            return Response(get_errormessage("REQ-104"), status=status.HTTP_400_BAD_REQUEST)
        contact_no = (phone[1:] if phone.startswith('0') else phone)
        customer = Customer.objects.filter(contact_no=contact_no).first()
        if not customer:
            return Response(get_errormessage("USER-101"), status=status.HTTP_400_BAD_REQUEST)
        response_code, response_status = customer.verify_otp(str(otp))
        data = dict(message=get_errormessage(response_code))
        if response_status == status.HTTP_202_ACCEPTED:
            refresh = RefreshToken.for_user(customer.user)
            data = dict(**data, id=customer.user.id, access=f"{refresh.access_token}")
        return Response(data, status=response_status)


class OTPverify(APIView):

    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        username = request.data.get('email')
        user = User.objects.filter(username=username).first()
        if not user:
            return Response(get_errormessage("USER-100"), status=status.HTTP_400_BAD_REQUEST)
        response_code, response_status = user.customer.verify_otp(otp)
        data = dict(message=get_errormessage(response_code))
        if response_status == status.HTTP_202_ACCEPTED:
            refresh = RefreshToken.for_user(user)
            data = dict(**data, id=user.id, access=f"{refresh.access_token}")
        return Response(data, status=response_status)


class SendCustomerNotificationView(APIView):

    def post(self, request, *args, **kwargs):
        customer_id = request.data['customer_id']
        customer = Customer.objects.get(pk=customer_id)
        send_customer_notification_email(customer, request.data)
        return Response({"message": "Success"})


class CustomerDashboardView(APIView):
    permission_classes = (IsCustomer,)

    def get(self, request):
        customer = get_current_user().customer
        context = {
        }
        return Response(context)
