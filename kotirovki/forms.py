__author__ = 'korvin'
# coding: utf-8
from django import forms
from apps.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate


class RegisterForm(forms.Form):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    # phone = forms.CharField()
    company = forms.CharField()
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def save(self):
        data = self.cleaned_data
        password = self.cleaned_data['password']
        del data['password']
        user = User.objects.create(**data)
        user.set_password(password)
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
            # try:
            self.user_cache = authenticate(username=username,password=password)
            if not self.user_cache:
                raise forms.ValidationError("Ошибка")
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Пользователь заблокирован')

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class PasswordRestoreForm(forms.Form):
    password = forms.CharField(required=True)
    password_confirm = forms.CharField(required=True)

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password_confirm != password:
            raise forms.ValidationError("Пароли не совпадают")
        return self.cleaned_data


class EditForm(forms.ModelForm):
    # first_name = forms.CharField(max_length=128)
    # last_name = forms.CharField(max_length=128)
    # birth_date = forms.DateTimeField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', ]

    # def save(self, commit=True):
    #     data = self.cleaned_data
    #     user = User(**data)
    #     user.save()








