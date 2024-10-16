from django.contrib import admin
from .models import *




@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'date_joined', 'last_login']

admin.site.register(OneTimePassword)
@admin.register(OneTimePassword)
class UserOneTimePassword(admin.ModelAdmin):
    list_display = ['all']

    