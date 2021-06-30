from django.conf.urls import url
from django.urls import include
from rest_framework import routers

import settings
from .views import *

if settings.DEBUG:
    router = routers.DefaultRouter()
else:
    router = routers.SimpleRouter()


router.register(r'role', RoleViewSet, basename='role')
router.register(r'custom-permission', CustomPermissionViewSet)


urlpatterns = [

    # registered api
    url(r'', include(router.urls)),
]
