from django.contrib import admin
from django.urls import path, include
from backtest import views
from user_strategy import views
urlpatterns = [
    path('user-strategy/', views.UserStrategyListApi.as_view(), name="user-strategy-list-api"),
    # path('admin/', admin.site.urls),
    # path('', include('all_api.urls')),
    # path('api/wandt/', include('wandt.urls')),
    # path('api/strategy/', include('user_strategy.urls')),

]
