from django.shortcuts import render
from .models import Strategy
from rest_framework.generics import ListAPIView
from .serializers import MarketPlaceStrategySerializer

# Create your views here.
class  UserStrategyListApi(ListAPIView):
    serializer_class = MarketPlaceStrategySerializer
    queryset = Strategy.objects.filter()
    
