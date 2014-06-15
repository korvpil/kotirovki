# coding: utf-8
from django.contrib import admin
from django.core.cache import get_cache
from django.contrib.admin import ListFilter
from .models import *
# noinspection PyUnresolvedReferences
from django.utils.translation import ugettext_lazy as _


class UserAdmin(admin.ModelAdmin):
    pass


class CompanyContactsAdmin(admin.ModelAdmin):
    # list_display = ('id', 'delivery', 'status', 'name', 'pay')
    # list_filter = ('status', 'delivery', 'pay')
    pass


class HeaderContactsAdmin(admin.ModelAdmin):
    pass


class HeaderMenuAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, UserAdmin)
admin.site.register(CompanyContacts, CompanyContactsAdmin)
admin.site.register(HeaderContacts, HeaderContactsAdmin)
admin.site.register(HeaderMenu, HeaderMenuAdmin)