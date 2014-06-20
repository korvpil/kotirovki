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


class LoginMixin(object):

    def get(self, request):
        if request.user.is_anonymous():
            return HttpResponseRedirect('/login/')
        return super(LoginMixin, self).get(self, request)


def login_req(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect('/login/')
    pass


class CommonData(TemplateView):

    def get_context_data(self, *args, **kwargs):
        context = super(CommonData, self).get_context_data()
        contacts = CompanyContacts.objects.get(id=1)
        menu = HeaderMenu.objects.all().order_by('sort')
        context['contacts'] = contacts
        context['menus'] = menu
        context['form'] = ''
        try:
            code = self.kwargs['code']
            context['is_grafik'] = True
        except:
            context['is_grafik'] = False
        print 'here'

        # Данные для построения графика на всех страницах
        if self.request.user.is_anonymous():
            my_data_1 = [300.0, 1267.0, 60.0, 229.0, 1292.0, 13000.0, 100.0, 2411.0, 1749.0, 5058.0, 1264.0, 9414.0, 457.0]
            my_data_2 = [300.0, 1267.0, 60.0, 229.0, 1292.0, 13000.0, 100.0, 2411.0, 1749.0, 5058.0, 1264.0, 9414.0, 457.0]
        else:
            my_data_1 = [457.0, 9414.0, 1264.0, 5058.0, 1749.0, 2411.0, 100.0, 0.0, 1292.0, 229.0, 60.0, 1267.0, 300.0]
            my_data_2 = [457.0, 9414.0, 1264.0, 5058.0, 1749.0, 2411.0, 100.0, 0.0, 1292.0, 229.0, 60.0, 1267.0, 300.0]

        context['my_data_1'] = my_data_1
        context['my_data_2'] = my_data_2
        # ================================================

        return context


class MultiMenuView(CommonData):
    template_name = 'multibox.html'

    def get_context_data(self, **kwargs):
        context = super(MultiMenuView, self).get_context_data()
        try:
            menu_type = HeaderMenu.objects.get(url='/'+self.kwargs['code']+'/')
            content = HeaderMenuContent.objects.get(menu=menu_type)
        except:
            return HttpResponseRedirect('/')
        context['is_feedback'] = False
        context['is_grafik'] = False
        if self.kwargs['code'] == 'feedback':
            if 'post' in kwargs:
                form = FeedBackForm(self.request.POST)
            else:
                form = FeedBackForm()
            context['form'] = form
            context['is_feedback'] = True

        if self.kwargs['code'] == 'grafik':
            try:
                pk = self.kwargs['pk']
            except:
                pk = StockType.objects.all().reverse()[0].pk

            stock_company = StockCompany.objects.filter(stock_type_id=pk)
            context['is_grafik'] = True
            context['items1'] = StockType.objects.all()
            context['items2'] = stock_company
        context['content_text'] = content
        if 'errors' in kwargs:
            context['errors'] = kwargs['errors']
        return context

    def post(self, request, code, **kwargs):
        form = FeedBackForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                feedback = FeedBack.objects.all().reverse()[0]
                text = "first_name - {0}" \
                       "last_name - {1}" \
                       "email - {2}" \
                       "text - {3}".format(feedback.first_name, feedback.last_name, feedback.email, feedback.text)
                msg = EmailMessage('email_confirmation', text, 'asf@mail.com', ["pilgrim.04@yandex.ru"])
                msg.content_subtype = "html"
                msg.send()
        else:
            kwargs['errors'] = "Ошибка. Заполните все поля!"
            kwargs['post'] = True
        return super(MultiMenuView, self).get(self, request, code, **kwargs)


class IsAuthenticated(object):

    def get(self, request):
        if not request.user.is_anonymous():
            return HttpResponseRedirect('/')
        return super(IsAuthenticated, self).get(self, request)


class IndexView(CommonData, TemplateView):
    template_name = 'index.html'

    def post(self, request):
        if request.POST.get('Login'):
            return HttpResponseRedirect('/login/')
        return super(IndexView, self).get(self, request)

    # def redirect(self, requset):
    #     return None


class RegisterView(CommonData, IsAuthenticated):
    form_class = RegisterForm
    template_name = 'registration.html'

    def get_context_data(self, **kwargs):
        # if not self.request.user.is_anonymous():
        #     return HttpResponseRedirect('/cabinet/')
        context = super(RegisterView, self).get_context_data()
        if 'errors' in kwargs:
            context['form'] = RegisterForm(self.request.POST)
        else:
            context['form'] = RegisterForm()
        if 'errors' in kwargs:
            context['errors'] = kwargs['errors']
        return context

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                email_confirm = EmailConfirmation.objects.create_for_user(form.save())
                text = 'http://{domain}/email/activate/{code}/'.format(domain=settings.DEFAULT_SERVER,
                                                                       code=email_confirm.code)
                msg = EmailMessage('email_confirmation', text, 'asf@mail.com', [email_confirm.user.email])
                msg.content_subtype = "html"
                msg.send()
                return HttpResponseRedirect('/logout/')
        else:
            kwargs['errors'] = True
            return super(RegisterView, self).get(self, request, *args, **kwargs)

    # def form_valid(self, form):
    #     form.save()
        # with transaction.atomic():
        #     Формирование письма активации аккаунта
            # email_confirm = EmailConfirmation.objects.create_for_user(form.save())
            # text = 'http://{domain}/email/activate/{code}/'.format(domain=settings.DEFAULT_SERVER,
            #                                                        code=email_confirm.code)
            # msg = EmailMessage('email_confirmation', text, 'asf@mail.com', [email_confirm.user.email])
            # msg.content_subtype = "html"
            # msg.send()
        # return HttpResponseRedirect('/logout/')
        # return super(RegisterView, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        kwargs['errors'] = 'Ошибка. Заполните все поля'
        return super(RegisterView, self).get(self, **kwargs)

class RequestRestorePassword(CommonData, TemplateView):
    template_name = 'request_restore_password.html'

    def get_context_data(self, *args, **kwargs):
        context = super(RequestRestorePassword, self).get_context_data(self, *args, **kwargs)
        if 'errors' in kwargs:
            context['errors'] = kwargs['errors']
        return context

    def post(self, request, *args, **kwargs):
        email = request.POST.get('restore_email')
        try:
            user = User.objects.get(email=unicode(email))
        except:
            kwargs['errors'] = 'Ошибка! Такой почты не зарегистрировано!'
            return super(RequestRestorePassword, self).get(self, request, *args, **kwargs)
        password_restore = PasswordRestore.objects.create_for_user(user)

        text = 'http://{domain}/password/restore/{code}/'.format(domain=settings.DEFAULT_SERVER,
                                                               code=password_restore.code)

        msg = EmailMessage('restore_password', text, 'asf@mail.com', [password_restore.user.email])
        msg.content_subtype = "html"
        msg.send()

        return HttpResponseRedirect('/')


# class FeedBackView(CommonData, FormView):

    # def get_context_data(self):
    #     context = super(FeedBackView, self).get_context_data()
    #     context
    #     return context

    # def form_valid(self, form):
    #     form.save()
    #     return super(FeedBackView, self).form_valid(self)


class LoginView(CommonData):
    form_class = LoginForm
    template_name = 'login.html'

    def get_context_data(self, *args, **kwargs):
        context = super(LoginView, self).get_context_data()
        if 'errors' in kwargs:
            context['form'] = LoginForm(self.request.POST)
        else:
            context['form'] = LoginForm()
        # if 'errors' in kwargs:
        #     context['errors'] = kwargs['errors']
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            if request.user and not request.user.is_anonymous():
                return HttpResponseRedirect('/cabinet/')
            auth_login(request, form.get_user())
            return HttpResponseRedirect('/cabinet/')
        else:
            # error = {}
            print form
            # if form.cleaned_data['username']:
            #     error = dict(error.items() +{'username':'Такого пользователя не существует'}.items())
            # if form.cleaned_data['password']:
            #     error = dict(error.items() +{'password':'Введите правильный пароль'}.items())
            # else:
            #     error = {'password': 'Заполните поле password', 'username': 'Заполните поле username'}
            kwargs['errors'] = True
        return super(LoginView, self).get(self, request, *args, **kwargs)

    # Авторизация
    # def form_valid(self, form):
    #     print 'gere'
    #     if self.request.user and not self.request.user.is_anonymous():
    #         raise Exception('Already login')
    #     auth_login(self.request, form.get_user())
    #     return HttpResponseRedirect('/cabinet/')


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


class CabinetView(CommonData):
    form_class = EditForm
    template_name = 'cabinet.html'

    def get_context_data(self, **kwargs):
        if self.request.user.is_anonymous():
            return HttpResponseRedirect('/login/')
        context = super(CabinetView, self).get_context_data()
        if 'post' in kwargs:
            context['form'] = EditForm(self.request.POST ,instance=self.request.user)
        else:
            context['form'] = EditForm(instance=self.request.user)
        # if 'errors' in kwargs:
        #     context['errors'] = kwargs['errors']
        return context

    def post(self, request, *args, **kwargs):
        form = EditForm(request.POST)
        if form.is_valid():
            user = self.request.user
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
        else:
            # kwargs['errors'] = 'Поле должно быть заполнено'
            kwargs['post'] = True
        return super(CabinetView, self).get(self, request, *args, **kwargs)

    # def form_valid(self, form):
    #     user = self.request.user
    #     user.first_name = form.cleaned_data.get('first_name')
    #     user.last_name = form.cleaned_data.get('last_name')
    #     user.save()
    #     return super(CabinetView, self).get(self)


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