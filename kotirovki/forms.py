__author__ = 'korvin'
# coding: utf-8

from django import forms
from apps.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate


class RegisterForm(forms.Form):
    username = forms.CharField()
    # first_name = forms.CharField()
    # last_name = forms.CharField()
    # phone = forms.CharField()
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def save(self):
        data = self.cleaned_data
        password = data['password']
        del data['password']
        user = User.objects.create_user(**data)
        user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    user_cache = None

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            print username
            print password
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Ошибка")
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Пользователь заблокирован')

        return self.cleaned_data

    def get_user(self):
        return self.user_cache