# coding: utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.utils import timezone
from hashlib import md5
from os import path as op
from time import time
import hashlib
from django.utils.timezone import now
import time
from random import randint
from django.conf import settings


def upload_to(instance, filename, prefix=None, unique=True):
    """
    Auto generate name for File and Image fields.
    :param instance: Instance of Model
    :param filename: Name of uploaded file
    :param prefix: Add to filename
    :param unique: Unique for the same instance and filename
    :return:
    """
    ext = op.splitext(filename)[1]
    name = str(instance.pk or '') + filename + (str(time()) if unique else '')

    # We think that we use utf8 based OS file system
    filename = md5(name.encode('utf8')).hexdigest() + ext
    basedir = op.join(instance._meta.app_label, instance._meta.module_name)
    if prefix:
        basedir = op.join(basedir, prefix)
    return op.join(basedir, filename[:2], filename[2:4], filename)


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField(default='1900-01-01')

    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now, verbose_name=u'Дата регистрации')
    company = models.CharField(max_length=128, null=True, verbose_name=u'Компания')

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'email']

    class Meta:
        verbose_name = u'Пользователь'
        verbose_name_plural = u'Пользователи'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class CompanyContacts(models.Model):
    description = models.TextField(max_length=128)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    copywrite_footer = models.CharField(max_length=128)

    class Meta:
        verbose_name = u'Контакт компании'
        verbose_name_plural = u'Контакты компании'


# Думаю можно удалить
class HeaderContacts(models.Model):
    logo = models.ImageField(blank=True, null=True, upload_to=upload_to)
    company_title = models.CharField(max_length=255)

    class Meta:
        verbose_name = u'Информация компании'
        verbose_name_plural = u'Информация компании'


class HeaderMenu(models.Model):
    title = models.CharField(max_length=128, verbose_name=u'Название меню')
    url = models.CharField(max_length=128, verbose_name=u'URL', help_text=u'URL необходимо вводить в формате :'
                                                                          u' /menu_name/')
    logo = models.ImageField(blank=True, null=True, upload_to=upload_to, verbose_name=u'Логотип')
    description = models.CharField(max_length=128 ,blank=True, null=True, verbose_name=u'Текстовое наполнение основного блока')

    class Meta:
        verbose_name = u'Меню в шапке'
        verbose_name_plural = u'Меню в шапке'


class Banners(models.Model):
    title = models.CharField(max_length=128, blank=True, null=True, verbose_name=u'Заголовок')
    img = models.ImageField(upload_to=upload_to, blank=True, null=True, verbose_name=u'Баннер')
    is_left = models.BooleanField(default=True, verbose_name=u'Располагать слева?', help_text=u'Установите флажок если '
                                                                                              u'нужно расположить'
                                                                                              u'баннер слева.'
                                                                                              u'Для расположения баннера'
                                                                                              u'справа флажок устанавлить ненужно.')


class EmailConfirmationManager(models.Manager):
    def create_for_user(self, user):
        code = hashlib.sha1(
            '{pk}_{time}_{salt}'.format(pk=user.pk, time=time.time(), salt=randint(1, 100000))).hexdigest()
        try:
            confirmation = self.get(user=user)
        except self.model.DoesNotExist:
            # noinspection PyCallingNonCallable
            confirmation = self.model(user=user, code=code)
        else:
            if (now() - confirmation.created_at).seconds > settings.EMAIL_CONFIRMATION_LIFETIME:
                confirmation.code = code
                confirmation.created_at = now()
        confirmation.save()
        return confirmation

    def get_by_code(self, code):
        confirmation = self.get(code=code)
        if (now() - confirmation.created_at).seconds > settings.EMAIL_CONFIRMATION_LIFETIME:
            confirmation.delete()
            raise self.model.DoesNotExist
        return confirmation


class EmailConfirmation(models.Model):
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=40, unique=True)

    objects = EmailConfirmationManager()

    def get_remote_url(self):
        return settings.CONFIRM_EMAIL_LINK.format(code=self.code)


class PasswordRestoreManager(models.Manager):
    def create_for_user(self, user):
        code = hashlib.sha1(
            '{pk}_{time}_{salt}'.format(pk=user.pk, time=time.time(), salt=randint(1, 100000))).hexdigest()
        try:
            confirmation = self.get(user=user)
        except self.model.DoesNotExist:
            # noinspection PyCallingNonCallable
            confirmation = self.model(user=user, code=code)
        else:
            if (now() - confirmation.created_at).total_seconds() > settings.RESTORE_PASSWORD_LIFETIME:
                confirmation.code = code
                confirmation.created_at = now()
        confirmation.save()
        return confirmation

    def get_by_code(self, code):
        confirmation = self.get(code=code)
        if (now() - confirmation.created_at).total_seconds() > settings.RESTORE_PASSWORD_LIFETIME:
            confirmation.delete()
            raise self.model.DoesNotExist
        return confirmation


class PasswordRestore(models.Model):
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(default=now())
    code = models.CharField(max_length=40, unique=True)

    objects = PasswordRestoreManager()

    def get_remote_url(self):
        return settings.RESTORE_PASSWORD_LINK.format(code=self.code)































