from django.contrib import admin
from .models import *
# Register your models here.

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'currency_name', 'description')


class IntervalAdmin(admin.ModelAdmin):
    list_display = ('id', 'minutes', 'description')


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Interval, IntervalAdmin)
