from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import AreaForm
from .models import Area

import logging

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'home/index.html')


@login_required
def index(request):
    return render(request, 'accounts/index.html')


def sign_up(request):
    context = {}
    form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'accounts/index.html')
    context['form'] = form
    return render(request, 'registration/sign_up.html', context)


def creat_area(request):
    context = {}
    form = AreaForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            area = form.save()
            return render(request, 'constant/area_list.html')
    context['form'] = form
    return render(request, 'constant/area.html', context)


def list_area(request):
    context = {}
    area = Area.objects.all()
    context['area'] = area
    return render(request, 'constant/area_list.html', context)
