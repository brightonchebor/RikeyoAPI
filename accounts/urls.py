from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('login/', LoginUserView.as_view(), name='login'),
    # path('profile/', TestAunthenticationView.as_view(), name='granted'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set-new-password'),
    path('logout/', LogoutUserView.as_view(), name='logout'),

    path('attendance/', AttendanceView.as_view(), name='mark-attendance'),

    path('<str:role>s/', UserListByRoleView.as_view(), name='all-users-list'),
    path('<str:role>/<int:id>/', SingleUserView.as_view(), name='single-user-detail'),
    path('attendance/history/', TeacherAttendanceHistoryView.as_view(), name='attendance-view'),
    path('attendance/history/?worker_id=<worker_id>/', TeacherAttendanceHistoryView.as_view(), name='attendance-view'),
    path('delete/<str:role>/<int:id>/', UserDeleteView.as_view(), name='delete user'),
    
]

