from datetime import date
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Strategy, FiveEMAStrategy
from django.contrib.auth.models import AnonymousUser

class UserStrategyListSerializer(ModelSerializer):
    class Meta:
        model = FiveEMAStrategy
        fields = ('id', 'running_date', 'running_time')

class MarketPlaceStrategySerializer(ModelSerializer):
    user_strategy = SerializerMethodField()
    class Meta:
        model = Strategy
        fields = ('id','name','minimum_amount', 'about', 'type', 'subscription_duration', 'updated_date', 'user_strategy')
        # fields = ('id','name','minimum_amount', 'about', 'type', 'subscription_duration', 'user_strategy')
        
    def get_user_strategy(self, obj):
        request = self.context.get("request")
        if request.user.is_authenticated:
            user_strategy_list = FiveEMAStrategy.objects.filter(user_id=request.user.id).filter(strategy_id=obj.id).filter(running_date=date.today(), status="Running").last()
            if user_strategy_list:
                user_strategy_strategy = UserStrategyListSerializer(user_strategy_list)
                return user_strategy_strategy.data
        return None