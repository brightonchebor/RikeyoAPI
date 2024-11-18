from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
from rest_framework_simplejwt.tokens import RefreshToken


AUTH_PROVIDERS = {'email':'email', 'google':'google', 'github':'github', 'facebook':'facebook'}
class User(AbstractBaseUser, PermissionsMixin):

    CHOICES = (
        ('manager', 'Manager'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin')
    )
    email = models.EmailField(max_length=255, unique=True, verbose_name=_("Email Address"))
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=15 ,choices=CHOICES, default='admin', db_index=True)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def tokens(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }

class OneTimePassword(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __srt__(self):
        return f'{self.user.first_name}-passcode'    

class Attendance(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    clock_in_time = models.DateTimeField(null=True, blank=True)  # Store clock-in time
    clock_out_time = models.DateTimeField(null=True, blank=True)  # Store clock-out time
    clock_in_location_latitude = models.FloatField(null=True, blank=True)  # Latitude for clock-in location
    clock_in_location_longitude = models.FloatField(null=True, blank=True)  # Longitude for clock-in location
    clock_out_location_latitude = models.FloatField(null=True, blank=True)  # Latitude for clock-out location
    clock_out_location_longitude = models.FloatField(null=True, blank=True)  # Longitude for clock-out location

    def __str__(self):
        return f'{self.user.first_name}, {self.user.last_name} - {self.date}'
    
    class Meta:
        unique_together = ('user', 'date')

class Geofence(models.Model):

    office_lat = models.IntegerField()
    office_long = models.IntegerField()
    geofence_radius = models.IntegerField()

    def __str__(self):
        return f'latitude:{self.office_lat}, longitude:{self.office_long}, radius:{self.geofence_radius}'