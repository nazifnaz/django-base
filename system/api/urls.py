from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers

from system.api.views import *

router = routers.DefaultRouter()
router.register(r'area', AreaViewSet)
router.register(r'country', CountryViewSet)
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'account-staffs', AccountStaffViewSet, basename='account_staff')
router.register(r'payment-status', PaymentStatusViewSet)
router.register(r'downloads', DownloadJobViewSet)
urlpatterns = [
    # registered api
    url(r'', include(router.urls)),
    path('change-password/', ChangePassword.as_view(), name='change_password'),
    path('change-profile-password/', ChangeProfilePassword.as_view(), name='change_profile_password'),
    path('document-types/', DocumentTypeApiView.as_view(), name='doc_types'),
]
