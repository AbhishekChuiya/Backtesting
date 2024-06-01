from users.views import UserDetailUpdateAPIView, UserDashboardApi
from django.urls import path, include

# urlpatterns : api/users/user-detail-update

urlpatterns = [

    path('user-detail-update/', UserDetailUpdateAPIView.as_view(), name='user-detail-update'),
    path('user-dashboard/', UserDashboardApi.as_view(), name='user-dashboard'),
]
