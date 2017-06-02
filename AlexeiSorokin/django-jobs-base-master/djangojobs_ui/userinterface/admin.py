# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from userinterface.models import Company, Errors, Vacancy


admin.site.register(Company)
admin.site.register(Errors)
admin.site.register(Vacancy)

