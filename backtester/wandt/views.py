from django.shortcuts import render
from .serializers import WandTStrategySerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from user_strategy.models import Strategy
from wandt.helper.start_stop_wt import start_wt_environment_set
from rest_framework import generics
from .models import InstrumentWandTStrategy, WandTStrategy
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .serializers import InstrumentWandTStrategySerializer, WandTStrategyUpdateSerializer
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

class WandTStrategyCreateView(APIView):
    def post(self, request):
        print(request.user)
        serializer = WandTStrategySerializer(data=request.data)
        if serializer.is_valid():
            wandtstrategy = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # if 'broker' in request.data :
        #     print(request.user)
        #     serializer = WandTStrategySerializer(data=request.data)
        #     if serializer.is_valid():
        #         wandtstrategy = serializer.save()
        #         # start_wt_environment_set(user_running_strategy_id = wandtstrategy.id)
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     # print(e)
        #     return Response(data='Broker is not added ',status=status.HTTP_400_BAD_REQUEST)

class InstrumentWandTStrategyListView(generics.ListAPIView):
    queryset = InstrumentWandTStrategy.objects.all()
    serializer_class = InstrumentWandTStrategySerializer

class WandTStrategyGetAllByUser(generics.ListAPIView):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]  # Add this line
    # permission_classes = [IsAuthenticated]  # Add this line
    pagination_class = None
    serializer_class = WandTStrategyUpdateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('status', 'running_date', 'running_time')

    def get_queryset(self):
        user = self.request.user
        print(user)
        print(user.pk)
        queryset = WandTStrategy.objects.filter(user_id=user.pk, is_deleted=False)
        # queryset = WandTStrategy.objects.filter(user_id=user.pk, is_deleted=False)
        print(queryset)
        return queryset
    
    
