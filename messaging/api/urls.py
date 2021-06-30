from django.urls import path, include
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet, FCMDeviceViewSet
from rest_framework.routers import DefaultRouter, SimpleRouter

import settings
from messaging.api.views import NotificationViewSet, NotificationTemplateViewSet, SendMessage

if settings.DEBUG:
    messaging_router = DefaultRouter()
else:
    messaging_router = SimpleRouter()

messaging_router.register('fcm_devices', FCMDeviceAuthorizedViewSet)

messaging_router.register('devices', FCMDeviceViewSet)

messaging_router.register('notifications', NotificationViewSet)
messaging_router.register('notifications-template', NotificationTemplateViewSet)

urlpatterns = [
    path('messaging/', include(messaging_router.urls)),
    path('messaging/send-message/', SendMessage.as_view(), name="send_message"),

]

