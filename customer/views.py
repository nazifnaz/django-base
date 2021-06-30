from django.shortcuts import render

# Create your views here.
from .forms import CustomerForm
from .models import Customer


def create_customer(request):
    context = {}
    form = CustomerForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            customer = form.save()
            return render(request, 'customer/list_customer.html')
    context['form'] = form
    return render(request, 'customer/create_customer.html', context)


def list_customer(request):
    context = {}
    customer = Customer.objects.all()
    context['customer'] = customer
    return render(request, 'customer/list_customer.html', context)


