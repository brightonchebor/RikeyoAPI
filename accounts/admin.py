from django.contrib import admin
from .models import *


admin.site.register(OneTimePassword)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'date_joined', 'last_login', 'role']

admin.site.register(Attendance)

admin.site.register(Geofence)

    