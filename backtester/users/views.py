from django.shortcuts import render
from .models import User
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from .serializers import UserUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from wandt.models import WandTStrategy
from wandt.serializers import WandTStrategySerializer
from django.db.models import Q
from datetime import date


# Create your views here.
class UserDetailUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        password = request.data.pop('password', None)
        email = request.data.pop('email', None)

        if password or email:
            return Response({'error': 'Password and email cannot be updated here'},
                            status=status.HTTP_400_BAD_REQUEST)

        return super().partial_update(request, *args, **kwargs)
    

class UserDashboardApi(APIView):
    
    def get(self, request):
        logged_in_user = self.request.user
        
        total_strategy_deployed_today = 0
        today_total_profit_loss = 0
        account_profit_loss = 0
        subscription_due_date = None
        deployed_strategy = {}
        
        # total_strategy_deployed_today =  FiveEMAStrategy.objects.filter(user_id = logged_in_user.id, running_date = date.today()).count() + WandTStrategy.objects.filter(user_id = logged_in_user.id, running_date = date.today()).count()
        
        # today_total_profit_loss = sum(WandTStrategyProfitLoss.objects.filter(status = "exit", wandtstrategy__running_date = date.today(), \
        #     wandtstrategy__user_id = logged_in_user.id).values_list('final_profit_loss', flat=True)) + sum(FiveEMAProfitLoss.objects.filter(strategy__user_id = logged_in_user.id, \
        #             strategy__running_date = date.today(), status = "exit").values_list('final_profit_loss', flat=True))
                
        # account_profit_loss = sum(WandTStrategyProfitLoss.objects.filter(status = "exit", \
        #     wandtstrategy__user_id = logged_in_user.id).values_list('final_profit_loss', flat=True)) + sum(FiveEMAProfitLoss.objects.filter(strategy__user_id = logged_in_user.id, \
        #             status = "exit").values_list('final_profit_loss', flat=True))
                
        # subscription_due_date = Subscription.objects.filter(user_id = logged_in_user.id).values('expiry_date')
        
        # five_ema_object =  FiveEMAStrategy.objects.filter(Q(user_id=logged_in_user.id, status__in=['Saved', 'Running'],is_deleted=False) | Q(user_id=logged_in_user.id, status='Stopped', running_date=date.today(),is_deleted=False))
        # five_ema_data = AllFiveEmaData(five_ema_object, many = True).data
        # deployed_strategy['five_ema'] = five_ema_data
        
        
        wait_and_trade_obj = WandTStrategy.objects.filter(Q(user_id=logged_in_user.id, status__in=['Saved', 'Running'],is_deleted=False) | Q(user_id=logged_in_user.id, status='Stopped', running_date=date.today(),is_deleted=False)).prefetch_related('w_t_strategy')
        wait_and_trade_data = WandTStrategySerializer(wait_and_trade_obj, many=True).data
        deployed_strategy['wait_and_trade'] = wait_and_trade_data
        
        
        data = {
            'total_strategy_deployed_today' : total_strategy_deployed_today,
            # 'today_total_profit_loss' : today_total_profit_loss,
            # 'account_profit_loss' : account_profit_loss,
            # 'subscription_due_date' : subscription_due_date,
            'deployed_strategy' : deployed_strategy
        }
        return Response(data)
    