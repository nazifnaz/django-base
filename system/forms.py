from django import forms
from .models import Area, Account


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['name']


class AccountCreate(forms.ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'reference', 'address', 'logo', ]