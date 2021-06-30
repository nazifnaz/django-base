import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated

from .filters import CartFilter
from .serializers import CartListSerializer, CartSerializer, ItemSerializer
from system.mixins import DownloadMixin
from ..models import Cart, Item

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ReadOnlyModelViewSet, DownloadMixin):
    permission_classes = (IsAuthenticated,)
    queryset = Cart.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CartFilter

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CartSerializer
        else:
            return CartListSerializer


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    authentication_classes = []
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
