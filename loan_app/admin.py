from django.contrib import admin

# Register your models here.

from .models import Bank, InterestRate, Option


admin.site.register(Bank)
admin.site.register(InterestRate)
admin.site.register(Option)
