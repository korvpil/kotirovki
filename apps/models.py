# coding: utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.utils import timezone
from hashlib import md5
from os import path as op
from time import time


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
    is_superuser = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'email']

    class Meta:
        verbose_name = u'Пользователь'
        verbose_name_plural = u'Пользователи'


class CompanyContacts(models.Model):
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    class Meta:
        verbose_name = u'Контакт компании'
        verbose_name_plural = u'Контакты компании'


class HeaderContacts(models.Model):
    logo = models.ImageField(blank=True, null=True, upload_to=upload_to)
    company_title = models.CharField(max_length=255)

    class Meta:
        verbose_name = u'Информация компании'
        verbose_name_plural = u'Информация компании'


import hashlib
from django.utils.timezone import now
import time
from random import randint
from django.conf import settings


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


