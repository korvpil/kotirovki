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

    is_active = models.BooleanField(default=True)
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