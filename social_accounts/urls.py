from djnago.urls import path
from .views import GoogleSignInView

urlpatterns = [
    path('google/', GoogleSignInView.as_view(), name='google')
]
