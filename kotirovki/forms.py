__author__ = 'korvin'
# coding: utf-8
from django import forms
from apps.models import *
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate


class RegisterForm(forms.Form):
    username = forms.CharField(required=False, label=u'Логин')
    first_name = forms.CharField(required=False, label=u'Имя')
    last_name = forms.CharField(required=False, label=u'Фамилия')
    # phone = forms.CharField()
    company = forms.CharField(required=False, label=u'Компания')
    email = forms.CharField(required=False, label=u'Электронный адрес')
    password = forms.CharField(widget=forms.PasswordInput, required=False, label=u'Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=False, label=u'Повторите пароль')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not username:
            raise forms.ValidationError('Введите логин')
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise forms.ValidationError('Введите имя')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise forms.ValidationError('Введите фамилию')
        return last_name

    def clean_company(self):
        company = self.cleaned_data['company']
        if not company:
            raise forms.ValidationError('Введите название компании')
        return company

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError('Введите адрес электронной почты')
        check_email = User.objects.filter(email=email)
        if check_email.exists():
            raise forms.ValidationError('Пользователь с такой почтой уже зарегистрирован')
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        if not password:
            raise forms.ValidationError('Введите пароль')
        return password

    def clean_password_confirm(self):
        password_confirm = self.cleaned_data['password_confirm']
        if not password_confirm:
            raise forms.ValidationError('Введите пароль повторно')
        return password_confirm

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        print password
        print password_confirm

        if password and password_confirm:
            if password_confirm != password:
                self._errors['password'] = u'Пароли не совпадают!'
                self._errors['password_confirm'] = u'Пароли не совпадают!'
                # raise forms.ValidationError('Пароли не совпадают!')
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        password = self.cleaned_data['password']
        del data['password']
        del data['password_confirm']
        user = User.objects.create(**data)
        user.set_password(password)
        user.save()

        return user


class LoginForm(forms.Form):
    username = forms.CharField(error_messages={'username':'Обязательное поле'}, required=False, label=u'Логин')
    password = forms.CharField(widget=forms.PasswordInput, required=False, label=u'Пароль')
    user_cache = None

    def clean_username(self):
        username = self.cleaned_data['username']
        if not username:
            raise forms.ValidationError('Введите логин')
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if not password:
            raise forms.ValidationError('Введите пароль')
        return password

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # try:
            self.user_cache = authenticate(username=username,password=password)
            if not self.user_cache:
                self._errors['username'] = u'Ошибка, неверный логин или пароль'
                # raise forms.ValidationError("Ошибка, неверный логин или пароль")
            elif not self.user_cache.is_active:
                self._errors['username'] = u'Пользователь заблокирован'
                # raise forms.ValidationError('Пользователь заблокирован')

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
    class Meta:
        model = User
        fields = ['first_name', 'last_name', ]

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise forms.ValidationError('Введите имя')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise forms.ValidationError('Введите фамилию')
        return last_name

    # def save(self, commit=True):
    #     data = self.cleaned_data
    #     user = User(**data)
    #     user.save()


class FeedBackForm(forms.ModelForm):
    # first_name = forms.CharField(required=False, label=u'Имя')
    # last_name = forms.CharField(required=False, label=u'Фамилия')
    # email = forms.CharField(required=False, label=u'Электронный адрес')
    # text = forms.CharField(widget=forms.Textarea,required=False, label=u'Текст')

    class Meta:
        model = FeedBack

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise forms.ValidationError('Введите имя')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise forms.ValidationError('Введите фамилию')
        return last_name

    def clean_text(self):
        text = self.cleaned_data['text']
        if not text:
            raise forms.ValidationError('Введите текст сообщения')
        return text

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError('Введите адрес электронной почты')
        return email

    def save(self, commit=True):
        data = self.cleaned_data
        feedback = FeedBack(**data)
        feedback.save()
        return feedback


