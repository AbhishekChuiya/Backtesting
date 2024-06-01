from django.db import models
from user_strategy.models import Strategy
from broker.models import TradingInstruments
from backtester.constants import OPTION_TYPE, order_type, trade_type_choice, position_type_choice, WANDT_TRADE_STATUS, ORDER_STATUS, ORDER_ENTRY_EXIT, ENTRY_EXIT_REASON, \
    TARGET_ON ,TARGET_UP_DOWN,WANDT_INSTRUMENT_PRODUCT_TYPE, SELECTION_TYPE, TARGET_TYPE, INSTRUMENT_IDS, STRICK_DISTANCE_GAP, CLOSEST_PREMIUM_TYPE, strategy_status,\
    STRATEGY_TYPE_CHOICES
from django.core.validators import MinValueValidator, MaxValueValidator

class WandTStrategy(models.Model):
    strategy_name = models.CharField(max_length=300, default='W&T')
    strategy_create_time = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    strategy_id = models.ForeignKey(Strategy, on_delete=models.SET_NULL, null=True, blank=True, related_name='strategy_wt_strategy')
    # broker = models.ForeignKey(UserBroker, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(choices=strategy_status, max_length=30, default='Saved')
    running_date = models.DateField(auto_now=True, null=True, blank=True)
    running_time = models.TimeField(auto_now=True, null=True, blank=True)
    # strategy_add_time= models.DateTimeField(auto_now_add=True,blank=True,null=True)
    is_deleted=models.BooleanField(default=False)
    # is_template=models.BooleanField(default=False)
    # strategy_type= models.CharField(choices=STRATEGY_TYPE_CHOICES,max_length=20,default='Bullish')
    #this is premium_group it will only trigger when all legs get entered.
    is_premium_group_calculate = models.BooleanField(default=False)
    premium_group =  models.FloatField(default=0.0)
    with_qty_group_premium = models.BooleanField(default=False)
    premium_group_exit_type = models.CharField(choices=TARGET_TYPE, max_length=10, default='POINTS')
    premium_group_target = models.FloatField(default=0.0)
    # current_group_premium=models.FloatField(default=0.0)
    premium_group_stoploss = models.FloatField(default=0.0)
    premium_target = models.FloatField(default=0.0)
    premium_stoploss = models.FloatField(default=0.0)
    re_entry_after_premium_exit = models.BooleanField(default=False)
    paper_trading= models.BooleanField(default=False)
    #mtom implementation parameters
    is_mtom_activated = models.BooleanField(default=False)
    mtom_target = models.FloatField(default=0.0)
    mtom_stop_loss = models.FloatField(default=0.0)
    mtom_trailing_sl = models.BooleanField(default=False)
    mtom_trailing_execute = models.BooleanField(default=False)
    mtom_trailing_value = models.FloatField(default=0.0) #if this value hit and trailing sl activated then we'll move sl target
    mtom_sl_movement = models.FloatField(default=0.0)
    mtom_target_movement = models.FloatField(default=0.0)

class InstrumentWandTStrategy(models.Model):
    instrument_name = models.CharField(choices=trade_type_choice, max_length=30)
    instrument_id = models.IntegerField(choices=INSTRUMENT_IDS)
    strick_distance_gap = models.IntegerField(choices=STRICK_DISTANCE_GAP)

class WandTStrategyLegs(models.Model):

    wandtstrategy = models.ForeignKey(WandTStrategy, on_delete=models.SET_NULL, null=True, blank=True, related_name='w_t_strategy')
    trading_instrument = models.ForeignKey(InstrumentWandTStrategy, on_delete=models.SET_NULL, null=True, blank=True, related_name='w_t_trading_inst')
    buy_sell_instrument =  models.ForeignKey(TradingInstruments, on_delete=models.SET_NULL, null=True, blank=True, related_name='buy_sell_instrument')
    qty = models.IntegerField(default=0)
    option_type = models.CharField(choices=OPTION_TYPE, max_length=10, default='CE')
    action_type = models.CharField(choices=order_type, max_length=10, default='BUY')
    start_time = models.TimeField(default='09:20')
    end_time = models.TimeField(default='15:18')
    selection_type = models.CharField(choices=SELECTION_TYPE, max_length=30, default='atm_point')
    strick_type = models.CharField(choices=position_type_choice, max_length=10, default='ATM')
    strick_distance = models.IntegerField(default=0)
    expiry_days =  models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(31)])
    expiry_month = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(12)])
    # expiry_year= models.IntegerField(default=2023,validators=[MinValueValidator(2023)])
    wait_and_trade = models.BooleanField(default=False)
    closest_premium_value = models.FloatField(default=0.0)
    closest_premium_type =  models.CharField(choices=CLOSEST_PREMIUM_TYPE, max_length=10, default='near')
    instrument_product = models.CharField(choices=WANDT_INSTRUMENT_PRODUCT_TYPE, max_length=10, default='MIS')
    target = models.FloatField(default=0.0)
    target_type = models.CharField(choices=TARGET_TYPE, max_length=10, default='POINTS')
    target_up_down = models.CharField(choices=TARGET_UP_DOWN, max_length=10, default='UP')
    is_entry_grouped = models.BooleanField(default=False)
    wait_and_trade = models.BooleanField(default=False)
    wait_and_trade_strick_price = models.FloatField(default=0.0)
    entry_spot_price = models.FloatField(default=0.0)
    entry_premium_price = models.FloatField(default=0.0)
    
    exit_spot_stop_loss = models.FloatField(default=0.0)
    exit_premium_stop_loss = models.FloatField(default=0.0)
    exit_spot_target = models.FloatField(default=0.0)
    exit_premium_target = models.FloatField(default=0.0)
    
    exit_target_on = models.CharField(choices=TARGET_ON, max_length=10, default='spot')
    exit_target_type = models.CharField(choices=TARGET_TYPE, max_length=10, default='POINTS')
    is_exit_grouped = models.BooleanField(default=False)
    
    exit_stop_loss = models.FloatField(default=0.0)
    exit_target = models.FloatField(default=0.0)
    
    trailing_sl = models.BooleanField(default=False)
    trailing_sl_target_type = models.CharField(choices=TARGET_TYPE, max_length=10, default='POINTS')
    trailing_sl_trigger_value = models.FloatField(default=0.0)
    trailing_sl_trigger_value_difference = models.FloatField(default=0.0)
    trailing_sl_movement = models.FloatField(default=0.0)
    trailing_target_movement = models.FloatField(default=0.0)
    # created_at= models.DateTimeField(auto_created=True,blank=True,null=True)
    re_execute = models.BooleanField(default=False) #create new lag with same parameter.
    re_entry = models.BooleanField(default=False) #need to wait till ltp come to same price for that given instrument.
    re_entry_execute_count = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)])
    re_entry_execute_calculate = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)])
    re_entry_execute_on_sl = models.BooleanField(default=False)
    re_entry_execute_on_target = models.BooleanField(default=False)
    current_trade_status = models.CharField(choices=WANDT_TRADE_STATUS, max_length=10, default='pending')
    is_auto_generated = models.BooleanField(default=False)

# class WandTStrategyLegsBuySell(models.Model):
#     wandtstrategy = models.ForeignKey(WandTStrategy, on_delete=models.SET_NULL, null=True, blank=True, related_name='w_t_strategy_buy_sell_logs')
#     wandtlagstrategy = models.ForeignKey(WandTStrategyLegs, on_delete=models.SET_NULL, null=True, blank=True, related_name='w_t_strategy_lag_buy_sell_logs')
#     order_type = models.CharField(choices=order_type, max_length=30, default='BUY')
#     qty = models.IntegerField(default=0)
#     order_date_time = models.DateTimeField(auto_now_add=True)
#     current_price = models.FloatField(null=True, blank=True)
#     order_place_id = models.CharField(max_length=150, null=True, blank=True)
#     instrument_id = models.BigIntegerField(default=0)
#     tradingsymbol = models.CharField(max_length=200, null=True, blank=True)
#     order_status = models.CharField(choices=ORDER_STATUS, max_length=30, default='pending')
#     entry_exit_flag = models.CharField(choices=ORDER_ENTRY_EXIT, max_length=30, default='entry')
#     entry_exit_reason =  models.CharField(choices=ENTRY_EXIT_REASON, max_length=30, default='direct_entry')

# class WandTStrategyProfitLoss(models.Model):
#     wandtstrategy = models.ForeignKey(WandTStrategy, on_delete=models.SET_NULL, null=True, blank=True, related_name='w_t_strategy_profit_losss')
#     wandtlagstrategy = models.ForeignKey(WandTStrategyLegs, on_delete=models.SET_NULL, null=True, blank=True, related_name='w_t_strategy_lag_profit_losss')
#     qty = models.IntegerField(default=0)
#     order_date_time = models.DateTimeField(auto_now_add=True)
#     instrument_id = models.BigIntegerField(default=0)
#     tradingsymbol = models.CharField(max_length=200, null=True, blank=True)
#     order_place_id = models.CharField(max_length=150, null=True, blank=True)
#     exit_order_place_id = models.CharField(max_length=150, null=True, blank=True)
#     entry_price = models.DecimalField(max_digits=8, decimal_places=4, default=0.00)
#     exit_price = models.DecimalField(max_digits=8, decimal_places=4, default=0.00)
#     final_profit_loss = models.DecimalField(max_digits=8, decimal_places=4, default=0.00)
#     status = models.CharField(choices=ORDER_ENTRY_EXIT, max_length=30, default='entry')
    
