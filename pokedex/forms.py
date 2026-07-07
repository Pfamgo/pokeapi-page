from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Region, Type


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class SearchForm(forms.Form):
    q = forms.CharField(required=False, label="Buscar")
    type = forms.ModelChoiceField(
        queryset=Type.objects.all(),
        required=False,
        empty_label="Todos los tipos",
        label="Tipo",
    )
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        empty_label="Todas las regiones",
        label="Región",
    )
