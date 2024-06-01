
from django.contrib import admin
from django.urls import path, include
# from rest_framework_simplejwt.views import TokenVerifyView

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
from backtest import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', include('all_api.urls')),
    # path('backtester/', include('Backtester.urls')),
    # path('api/wandt/', include('wandt.urls')),
    # path('api/strategy/', include('user_strategy.urls')),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('backtest/', views.backtest2, name="backtest"),
    # path('preprocess/', views.PreprocessView.as_view(), name='preprocess'),

]
