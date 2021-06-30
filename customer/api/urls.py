from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()

router.register(r'customer', CustomerViewSet, basename='customer')
router.register(r'customers/address', AddressViewSet)


urlpatterns = [
    # registered api
    url(r'', include(router.urls)),

    # customer
    path('customers/login/', CustomerLoginView.as_view(), name='login_customers'),
    path('customers/logout/', CustomerLogoutView.as_view(), name='logout_customers'),
    path('customers/change-status/', ChangeCustomerStatus.as_view(), name='change_customer_status'),
    path('customers/change-password/', ChangePassword.as_view(), name='customer_change_password'),
    path('forgot-password/', ResetPassword.as_view(), name='reset_password'),
    path('otp-verify/', OTPverify.as_view(), name='otp_verify'),
    path('customers/send-notification/', SendCustomerNotificationView.as_view(), name='send_notification'),
    path('customers/dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),

    # staff
    path('staff/login/', StaffLoginView.as_view(), name='staff_login'),
    path('user/permissions/', UserPermissionView.as_view(), name='user_permission'),

    # Validation API
    path('validate-data/', UniqueValidationView.as_view(), name='validate_data'),

]
