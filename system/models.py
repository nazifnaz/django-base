from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from django_currentuser.middleware import get_current_authenticated_user

from constants import DOWNLOAD_HANDLERS, DOWNLOAD_STATUS
from system.paths import get_account_path, get_document_storage_path, get_download_path
from system.services import unique_id


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name="created_%(app_label)s_%(class)s",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name="updated_%(app_label)s_%(class)s",
        on_delete=models.SET_NULL,
    )
    history = HistoricalRecords(inherit=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.created_by = get_current_authenticated_user()
        self.updated_by = get_current_authenticated_user()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['created_at']


class BaseModelBeforeHistory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name="created_%(app_label)s_%(class)s",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name="updated_%(app_label)s_%(class)s",
        on_delete=models.SET_NULL,
    )

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.created_by = get_current_authenticated_user()
        self.updated_by = get_current_authenticated_user()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Country(BaseModelBeforeHistory):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    isd_code = models.CharField(max_length=3)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class DocumentType(BaseModelBeforeHistory):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Document(BaseModel):
    document = models.FileField(upload_to=get_document_storage_path, blank=True, null=True)
    document_type = models.ForeignKey(DocumentType, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True

    @property
    def document_type_ar(self):
        return self.document_type.name_ar if self.document_type else ''

    @property
    def document_type_en(self):
        return self.document_type.name_en if self.document_type else ''


class Account(BaseModel):
    name = models.CharField(max_length=50)
    contact_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    city = models.CharField(max_length=100, null=True, blank=True, default='')
    pb_no = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, related_name='accounts', blank=True, null=True,
                                on_delete=models.SET_NULL)
    address = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to=get_account_path, blank=True, null=True)
    reference = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_encryption_key(self):
        if hasattr(self, 'keys'):
            return self.keys.last()
        return None

    class Meta:
        ordering = ['-is_active', 'created_at']

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = unique_id('ACC')
        return super(Account, self).save(*args, **kwargs)


class AbstractStaff(BaseModel):
    from role.models import Role
    contact_no = models.CharField(max_length=20, null=True, blank=True)
    user = models.OneToOneField(User, related_name='%(class)s', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    role = models.ForeignKey(Role, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True
        ordering = ['-is_active', 'created_at']

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email


class AccountStaff(AbstractStaff):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.id)

    @property
    def role_display(self):
        return self.get_role_display()


class ErrorMessage(BaseModelBeforeHistory):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=240, null=True, blank=True)

    def _str_(self):
        return f"{self.name}-{self.code}"


class CartStatus(BaseModel):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class PaymentStatus(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Area(BaseModelBeforeHistory):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.PROTECT)
    has_cod = models.BooleanField(default=True)
    paci_neighboorhood_id = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Configuration(BaseModel):
    email_type = models.PositiveSmallIntegerField(choices=((1, 'Default'), (2, 'SMTP'), (3, 'SENDGRID')), default=1)
    sender_email = models.CharField(max_length=255, blank=True, null=True, help_text="Should be verified")
    smtp_username = models.CharField(max_length=255, blank=True, null=True)
    smtp_password = models.CharField(max_length=255, blank=True, null=True)
    smtp_host = models.CharField(max_length=255, blank=True, null=True)
    smtp_port = models.CharField(max_length=255, blank=True, null=True)
    sendgrid_api_key = models.CharField(max_length=255, blank=True, null=True)
    sms_type = models.PositiveSmallIntegerField(choices=((1, 'Default'), (2, 'Local'), (2, 'International')), default=1)
    sender_sms = models.CharField(max_length=255, blank=True, null=True, help_text="Should be verified")


class BlackListedToken(BaseModel):
    token = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)


class DownloadJob(BaseModel):
    STATUS = (
        (DOWNLOAD_STATUS.INITIATED, 'Initiated'),
        (DOWNLOAD_STATUS.IN_QUEUE, 'In queue'),
        (DOWNLOAD_STATUS.PROCESSING, 'Processing'),
        (DOWNLOAD_STATUS.PROCESSED, 'Processed'),
        (DOWNLOAD_STATUS.FAILED, 'Failed'),
        (DOWNLOAD_STATUS.CANCELLED, 'Cancelled'),
    )
    DOWNLOAD_SOURCE = ((value, key) for key, value in dict(DOWNLOAD_HANDLERS).items())
    request_data = models.JSONField(null=True, blank=True)
    download_type = models.SmallIntegerField(choices=DOWNLOAD_SOURCE, default=1)
    status = models.SmallIntegerField(choices=STATUS, default=DOWNLOAD_STATUS.INITIATED)
    started_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    files = models.FileField(upload_to=get_download_path, blank=True, null=True)
    complete_percentage = models.IntegerField(default=1, blank=True)
    data_count = models.IntegerField(default=0, blank=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at', '-id']

    def __str__(self):
        return '%s' % self.created_by

    def is_processed(self):
        return self.status == DOWNLOAD_STATUS.PROCESSED

    def in_queue(self):
        self.status = DOWNLOAD_STATUS.IN_QUEUE
        self.save()

    def processing(self):
        self.status = DOWNLOAD_STATUS.PROCESSING
        self.save()

    def failed(self):
        self.status = DOWNLOAD_STATUS.FAILED
        self.save()

    def processed(self):
        self.status = DOWNLOAD_STATUS.PROCESSED
        self.save()
