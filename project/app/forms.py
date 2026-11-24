
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.core.validators import MinLengthValidator, MaxLengthValidator



class SignUpForm(UserCreationForm):
    username = forms.CharField(
        min_length=settings.USERNAME_MINLENGTH,
        max_length=settings.USERNAME_MAXLENGTH,
        error_messages={
            'min_length': f'Username must contain at least {settings.USERNAME_MINLENGTH} characters.',
            'max_length': f'Username cannot exceed {settings.USERNAME_MAXLENGTH} characters.',
        },
    )
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

#use custom-made signup form to bypass all the security checks that the UserCreationForm provides
#A07:2021 – Identification and Authentication Failures: Permits default, weak, or well-known passwords, such as "Password1" or "admin/admin"
class CustomSignUpForm(forms.Form):
    username = forms.CharField()
    password1 = forms.CharField()


class SignInForm(forms.Form):
    username = forms.CharField(
        min_length=settings.USERNAME_MINLENGTH,
        max_length=settings.USERNAME_MAXLENGTH,
        error_messages={
            'min_length': f'Username must contain at least {settings.USERNAME_MINLENGTH} characters.',
            'max_length': f'Username cannot exceed {settings.USERNAME_MAXLENGTH} characters.',
        },
        )
    password = forms.CharField(
        min_length=settings.PASSWORD_MINLENGTH,
        error_messages={
            'min_length': f'Password must contain at least {settings.PASSWORD_MINLENGTH} characters.'
        },
        widget=forms.PasswordInput
        )
    
