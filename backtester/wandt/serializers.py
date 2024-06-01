from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from drf_writable_nested import NestedUpdateMixin
from .models import WandTStrategyLegs, WandTStrategy, InstrumentWandTStrategy

class WandTStrategyLegsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WandTStrategyLegs
        fields = '__all__'

class WandTStrategySerializer(serializers.ModelSerializer):
    w_t_strategy = WandTStrategyLegsSerializer(many=True)

    class Meta:
        model = WandTStrategy
        fields = '__all__'

    def create(self, validated_data):
        w_t_strategy_legs_data = validated_data.pop('w_t_strategy')
        wandtstrategy = WandTStrategy.objects.create(**validated_data)

        for legs_data in w_t_strategy_legs_data:
            WandTStrategyLegs.objects.create(wandtstrategy=wandtstrategy, **legs_data)

        return wandtstrategy
    
class InstrumentWandTStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentWandTStrategy
        fields = '__all__'

class WandTStrategyLegsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WandTStrategyLegs
        fields = '__all__'

class WandTStrategyUpdateSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    w_t_strategy = WandTStrategyLegsUpdateSerializer(many=True)

    class Meta:
        model = WandTStrategy
        fields = '__all__'
