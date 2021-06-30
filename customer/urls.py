

from django.urls import path
from . import views



urlpatterns = [
    path('customer/list', views.list_customer, name="list_customer"),
    path('customer/create', views.create_customer, name="create_customer"),


]