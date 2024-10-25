from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile/', TestAunthenticationView.as_view(), name='granted'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set-new-password'),
    path('logout/', LogoutUserView.as_view(), name='logout'),

    path('attendance/', AttendanceView.as_view(), name='attendance'),

    path('teachers/', AllTeachers.as_view(), name='all-teachers'),
    path('managers/', AllManagers.as_view(), name='all-managers'),
    path('api/users/<str:role>/<int:id>/', SingleUserView.as_view(), name='user-detail'),
]

