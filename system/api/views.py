import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_currentuser.middleware import get_current_user
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, filters, status, views
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from constants import ACCOUNT_ROLES, DOWNLOAD_STATUS
from system.api.filters import DownloadJobFilter, AccountFilter, AccountStaffFilter
from system.api.serializer import AccountListSerializer, AccountSerializer, AccountStaffSerializer,  AreaSerializer, \
    CountrySerializer, PaymentStatusModeSerializer, DocumentTypeSerializer, DownloadJobSerializer
from system.models import Account, AccountStaff, Area, Country, PaymentStatus, DocumentType, \
    DownloadJob
from system.services import create_staff, update_staff, cancel_task, is_account, get_account
from system.user_permissions import IsAccount
from system.utils import get_errormessage

logger = logging.getLogger(__name__)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    permission_classes = (IsAccount,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AccountFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountListSerializer
        else:
            return AccountSerializer

    def perform_create(self, serializer):
        account = serializer.save()
        self.create_account_docs(account)
        create_staff(self.get_user_data(account), AccountStaffSerializer)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        errors = self.perform_update(serializer)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.data)

    def get_user_data(self, account):
        return {
            'email': account.email,
            'first_name': account.id_name,
            'contact_no': account.contact_no,
            'account_id': account.id,
            'role_id': ACCOUNT_ROLES.ADMIN,
        }

    @action(methods=['post', ], detail=True)
    def update_status(self, request, pk):
        instance = self.get_object()
        instance.is_active = request.data['is_active']
        instance.save()
        return Response({"message": "Success"})


class AccountStaffViewSet(viewsets.ModelViewSet):
    queryset = AccountStaff.objects.all()
    serializer_class = AccountStaffSerializer
    permission_classes = (IsAccount,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AccountStaffFilter

    def get_queryset(self):
        current_user = self.request.user
        if is_account(current_user):
            return self.queryset.filter(account=get_account(current_user)).exclude(user=current_user)
        return self.queryset

    def create(self, request, *args, **kwargs):
        return create_staff(request.data, self.get_serializer)

    def update(self, request, *args, **kwargs):
        data = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        return update_staff(instance.user, data, serializer)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', ], detail=True)
    def update_status(self, request, pk):
        instance = self.get_object()
        if instance.user == request.user:
            return Response(get_errormessage('USER-104'), status=status.HTTP_400_BAD_REQUEST)
        instance.is_active = request.data['is_active']
        instance.save()
        return Response({"message": "Success"})


class AreaViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    pagination_class = None

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['id', 'country']
    search_fields = ['name']


class CountryViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Country.objects.exclude(id=206)
    serializer_class = CountrySerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    authentication_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['id', 'name', 'code']
    search_fields = ['name']


class PaymentStatusViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = PaymentStatus.objects.all()
    serializer_class = PaymentStatusModeSerializer
    pagination_class = None


class ChangePassword(views.APIView):
    permission_classes = (IsAccount,)

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        new_password = request.data.get('password')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error_en": "User does not exist",
                             "error_ar": "المستخدم غير موجود"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        context = {
            'message': 'Password updated successfully',
        }
        return Response(context, status=status.HTTP_200_OK)


class ChangeProfilePassword(views.APIView):
    permission_classes = (IsAccount,)

    def post(self, request, *args, **kwargs):
        current_user = get_current_user()
        username = current_user.username
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        user = authenticate(username=username, password=old_password)
        if user:
            user.set_password(new_password)
            user.save()
            context = {
                'message': 'Password updated successfully',
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            context = {
                'error_en': 'old password is wrong',
                'status': status.HTTP_400_BAD_REQUEST
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class DocumentTypeApiView(views.APIView):
    permission_classes = ()

    def get(self, request):
        # Add document type filter based on screen
        doc_type = request.GET.get('type', None)
        doc_types = DocumentType.objects.filter()
        serializer = DocumentTypeSerializer(doc_types, many=True)
        return Response(serializer.data)


class DownloadJobViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = DownloadJob.objects.all()
    serializer_class = DownloadJobSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DownloadJobFilter

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        retry = request.GET.get('retry', None)
        cancel = request.GET.get('cancel', None)
        if retry == "true":
            from system.tasks import execute_download
            task = execute_download.delay(instance.id)

        if cancel == "true":
            if instance.task_id:
                cancel_task(instance.task_id)
                instance.status= DOWNLOAD_STATUS.CANCELLED
                instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
