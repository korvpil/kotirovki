__author__ = 'korvin'
from django.http import HttpResponseRedirect, HttpResponse
from apps.models import *
from django.views.generic import FormView, View, ListView, DetailView, UpdateView
from django.contrib.auth import login as auth_login, logout as auth_logout
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
            email_confirm = EmailConfirmation.objects.create_for_user(form.save())
            text = 'http://{domain}/email/activate/{code}/'.format(domain=settings.DEFAULT_SERVER,
                                                                   code=email_confirm.code)
            msg = EmailMessage('email_confirmation', text, 'asf@mail.com', [email_confirm.user])
            msg.content_subtype = "html"
            msg.send()
        return HttpResponseRedirect('/login/')


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        if self.request.user.is_authenticated():
            raise Exception('Already login')
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect('/')


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect('/')


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
