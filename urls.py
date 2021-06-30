from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)

router = DefaultRouter()

router.register(r'api/devices', FCMDeviceAuthorizedViewSet)


urlpatterns = [


    path('', include("system.urls")),
    # Admin Level

    url(r'^admin/', admin.site.urls),

    # customer apis
    url('api/', include('customer.api.urls'), name='customer'),
    url('api/', include('system.api.urls')),
    url('api/', include('messaging.api.urls')),
    url('api/', include('role.api.urls')),

    # Internal Views

    path('customer/', include("customer.urls")),
    path('accounts/', include('django.contrib.auth.urls')),

    # Token Generate
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

if settings.DEV_MODE:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
