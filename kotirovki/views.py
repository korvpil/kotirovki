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


def login_req(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect('/login/')
    pass


class CommonData(TemplateView):

    def get_context_data(self):
        context = super(CommonData, self).get_context_data()
        contacts = CompanyContacts.objects.get(id=1)
        menu = HeaderMenu.objects.all()
        context['contacts'] = contacts
        context['menus'] = menu

        # Данные для построения графика на всех страницах
        my_data_1 = [300.0, 1267.0, 60.0, 229.0, 1292.0, 13000.0, 100.0, 2411.0, 1749.0, 5058.0, 1264.0, 9414.0, 457.0]
        my_data_2 = [300.0, 1267.0, 60.0, 229.0, 1292.0, 13000.0, 100.0, 2411.0, 1749.0, 5058.0, 1264.0, 9414.0, 457.0]

        context['my_data_1'] = my_data_1
        context['my_data_2'] = my_data_2
        # ================================================

        return context


class MultiMenuView(CommonData, TemplateView):
    template_name = 'multibox.html'

    def get_context_data(self, **kwargs):
        context = super(MultiMenuView, self).get_context_data()
        try:
            menu_type = HeaderMenu.objects.get(title=self.kwargs['code'])
        except:
            return HttpResponseRedirect('/')
        context['content_text'] = menu_type.description
        return context


class IsAuthenticated(object):

    def get(self, request):
        if not request.user.is_anonymous():
            return HttpResponseRedirect('/')
        return super(IsAuthenticated, self).get(self, request)


class LoginMixin(object):

    def get(self, request):
        if request.user.is_anonymous():
            return HttpResponseRedirect('/login/')
        return super(LoginMixin, self).get(self, request)


class IndexView(CommonData, TemplateView):
    template_name = 'index.html'

    def post(self, request):
        if request.POST.get('Login'):
            return HttpResponseRedirect('/login/')
        return super(IndexView, self).get(self, request)

    # def redirect(self, requset):
    #     return None


class RegisterView(CommonData, IsAuthenticated, FormView):
    form_class = RegisterForm
    template_name = 'registration.html'

    def get_context_data(self, **kwargs):
        # if not self.request.user.is_anonymous():
        #     return HttpResponseRedirect('/cabinet/')
        context = super(RegisterView, self).get_context_data()
        context['form'] = self.form_class
        return context

    def form_valid(self, form):
        # form.save()
        with transaction.atomic():
            # Формирование письма активации аккаунта
            email_confirm = EmailConfirmation.objects.create_for_user(form.save())
            text = 'http://{domain}/email/activate/{code}/'.format(domain=settings.DEFAULT_SERVER,
                                                                   code=email_confirm.code)
            msg = EmailMessage('email_confirmation', text, 'asf@mail.com', [email_confirm.user.email])
            msg.content_subtype = "html"
            msg.send()
        return HttpResponseRedirect('/logout/')


class RequestRestorePassword(CommonData, TemplateView):
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


class LoginView(CommonData, FormView):
    form_class = LoginForm
    template_name = 'login.html'

    def get_context_data(self):
        context = super(LoginView, self).get_context_data()
        context['form'] = LoginForm
        return context

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


class PasswordRestoreView(CommonData ,TemplateView):
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


class CabinetView(CommonData ,FormView):
    form_class = EditForm
    template_name = 'cabinet.html'

    def get_context_data(self, **kwargs):
        if self.request.user.is_anonymous():
            return HttpResponseRedirect('login/')


        context = super(CabinetView, self).get_context_data()
        context['form'] = self.form_class
        return context

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.save()
        return super(CabinetView, self).get(self)


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


class GrafikiView(TemplateView):
    template_name = 'grafiki.html'

    def get_context_data(self, **kwargs):
        context = super(GrafikiView, self).get_context_data(**kwargs)
        my_data_1 = [300.0, 1267.0, 60.0, 229.0, 1292.0, 13000.0, 100.0, 2411.0, 1749.0, 5058.0, 1264.0, 9414.0, 457.0]

        my_data_2 = [300.0, 1267.0, 60.0, 229.0, 1292.0, 13000.0, 100.0, 2411.0, 1749.0, 5058.0, 1264.0, 9414.0, 457.0]

        context['my_data_1'] = my_data_1
        context['my_data_2'] = my_data_2

        return context