from django.conf.urls import url
from django.urls import include

from order.api.views import ItemViewSet, CartViewSet
from urls import router

router.register(r'item', ItemViewSet)
router.register(r'cart', CartViewSet)

urlpatterns = [
    # registered api
    url(r'', include(router.urls)),
]
