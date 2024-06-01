
from django.contrib import admin
from django.urls import path, include
from . import views

#URL - http://127.0.0.1:8000/api/wandt/instruments
urlpatterns = [
    path('wandtstrategy/', views.WandTStrategyCreateView.as_view(), name='wandtstrategy-create'),
    path('instruments/', views.InstrumentWandTStrategyListView.as_view(), name='instrument-list'),
    # path('wt-buy-sell-logs/<int:wandtstrategy_id>/', views.WandTStrategyLegsBuySellViewSet.as_view(), name="wt-buy-sell-logs"),
    # path('wt-profit-loss/<int:wandtstrategy_id>/', views.WandTStrategyProfitLossViewSet.as_view(), name="wt-profit-loss-logs"),
    path('wt-get-all-by-user/', views.WandTStrategyGetAllByUser.as_view(), name="wt-get-all-by-user"),

]
