from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView
# from .views import UserRetrieveAPIView

urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('signup/', views.UserSignUp.as_view({'post': 'create'}), name='signup'),
    path('forgot/', views.ForgotPasswordView.as_view(), name='forgot'),
    path('reset/', views.ResetPasswordView.as_view(), name='reset'),
    # path('csv/', views.JSONtoCSV.as_view(), name='csv'),
    path('reset-password/', include('django.contrib.auth.urls')),  
    path('api-auth/', include('rest_framework.urls')), 
    # path('users/<str:username>/', UserRetrieveAPIView.as_view(), name='user-detail'),

]
