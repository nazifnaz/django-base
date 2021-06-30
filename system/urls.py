from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.home, name="home"),
    path('accounts/', include('django.contrib.auth.urls'), name="login"),
    path('accounts/sign_up/', views.sign_up, name="sign-up"),
    path('constant/area/create', views.creat_area, name="area_create"),
    path('constant/area/list', views.list_area, name="area_list"),
]