__author__ = 'korvin'
# coding: utf-8
from django.http import HttpResponseRedirect
from apps.models import *
from django.views.generic import FormView, View
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.views.generic import TemplateView
from .forms import *
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.db import transaction
from django.conf import settings


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration.html'

    def form_valid(self, form):
        with transaction.atomic():
            # Формирование письма активации аккаунта
            email_confirm = EmailConfirmation.objects.create_for_user(form.save())
            text = 'http://{domain}/email/activate/{code}/'.format(domain=settings.DEFAULT_SERVER,
                                                                   code=email_confirm.code)
            msg = EmailMessage('email_confirmation', text, 'asf@mail.com', [email_confirm.user.email])
            msg.content_subtype = "html"
            msg.send()
        return HttpResponseRedirect('/logout/')


class RequestRestorePassword(TemplateView):
    template_name = 'request_restore_password.html'

    def post(self, request):
        email = request.POST.get('restore_email')
        try:
            user = User.objects.get(email=unicode(email))
        except:
            raise
        password_restore = PasswordRestore.objects.create_for_user(user)

        text = 'http://{domain}/password/restore/{code}/'.format(domain=settings.DEFAULT_SERVER,
                                                               code=password_restore.code)

        msg = EmailMessage('restore_password', text, 'asf@mail.com', [password_restore.user.email])
        msg.content_subtype = "html"
        msg.send()

        return HttpResponseRedirect('/')


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'

    # Авторизация
    def form_valid(self, form):
        if self.request.user and not self.request.user.is_anonymous():
            raise Exception('Already login')
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect('/cabinet/')


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect('/login/')


class PasswordRestoreView(TemplateView):
    template_name = 'restore_password.html'

    # Проверка кода авторизации
    def get_context_data(self, **kwargs):
        context = super(PasswordRestoreView, self).get_context_data()
        code = self.kwargs['code']
        self.restore_password(code)
        context['form'] = PasswordRestoreForm
        return context

    def restore_password(request, code):
        try:
            password_restore = PasswordRestore.objects.get_by_code(code=unicode(code))
            return password_restore
        except:
            raise

    # Смена пароля
    def post(self, request, *args, **kwargs):
        form = PasswordRestoreForm(self.request.POST)
        if form.is_valid():
            with transaction.atomic():
                password_restore = self.restore_password(kwargs['code'])
                user = password_restore.user
                user.set_password(form.cleaned_data['password'])
                user.save()
                password_restore.delete()
            return HttpResponseRedirect('/cabinet/')

        return super(PasswordRestoreView, self).get(self, *args, **kwargs)


class CabinetView(TemplateView):
    template_name = 'cabinet.html'

    def get_context_data(self, **kwargs):
        if self.request.user.is_anonymous():
            return HttpResponseRedirect('login/')

        # return super(CabinetView, self).get_context_data(self, **kwargs)


# Активация аккаунта
def activate_account(request, code):
    EmailConfirmation.objects.get_by_code(code=unicode(code))
    try:
        emailconfirm = EmailConfirmation.objects.get_by_code(code=unicode(code))
        user = emailconfirm.user
        user.is_active = True
        user.save()
        emailconfirm.delete()
        return HttpResponseRedirect('/login/')
    except:
        return HttpResponseRedirect('/email/activate/')
