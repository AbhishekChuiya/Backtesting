from django.db import models
from backtester.constants import strategy_status, type, candle_size, SEGMENT_TYPE,INSTRUMENT_PRODUCT_TYPE, option_status, order_type, \
    call_put, ORDER_ENTRY_EXIT, ORDER_STATUS, trade_type_choice, position_type_choice,indicators_type_choices,candle_size_choices,\
    sl_count_choices,target_count_choices,buffer_type_choices
from django.core.validators import MinValueValidator, MaxValueValidator


class Strategy(models.Model):
    name= models.CharField(max_length=50, null=True, blank=True)
    minimum_amount= models.FloatField(max_length=100, null=True, blank=True)
    about=models.TextField(null=True, blank=True)
    # status=models.BooleanField(default=False)
    type = models.CharField(choices=type, max_length=30, default='OptionBuying')
    subscription_duration=models.FloatField(max_length=100, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    # is_deleted = models.BooleanField(default=False)

class UserSubscribedStrategy(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    

class FiveEMAStrategy(models.Model):
    strategy_name = models.CharField(max_length=100, default="FiveEMA")
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    strategy_id = models.ForeignKey(Strategy, on_delete=models.CASCADE, null=True, blank=True, related_name='strategy_five_ema_strategy')
    # broker = models.ForeignKey(UserBroker, on_delete=models.CASCADE, null=True, blank=True)
    instrument_id = models.IntegerField(null=True, blank=True)
    tradingsymbol = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(choices=strategy_status, max_length=30, default='Stopped')
    running_date = models.DateField(auto_now=True, null=True, blank=True)
    running_time = models.TimeField(auto_now=True, null=True, blank=True)
    qty = models.IntegerField(default=0)
    ema_period = models.IntegerField(default=5)
    ema_timeframe = models.CharField(choices=candle_size,max_length=100, default="5")
    target_multiplier = models.FloatField(null=True, blank=True)
    target_count_type= models.CharField(max_length=50,choices=target_count_choices,blank= True,null=True)
    # target_count_value=models.FloatField(blank=True,null=True)
    # bp_level_value= models.FloatField(blank=True,null=True)
    max_trades = models.IntegerField(null=True, blank=True)
    is_deletd= models.BooleanField(default=False)
    indicator_type= models.CharField(max_length=100,choices=indicators_type_choices,default='EMA',blank=True,null=True)
    trade_type = models.CharField(choices=trade_type_choice,max_length=100, default="BANKNIFTY")
    position_type =  models.CharField(choices=position_type_choice,max_length=100, default="ATM")
    expiry_days =  models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(31)])
    expiry_month = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(12)])
    expiry_year= models.IntegerField(default=2023,validators=[MinValueValidator(2023)])
    strick_distance = models.IntegerField(default=0)
    segment = models.CharField(choices=SEGMENT_TYPE,max_length=100, default="cash")
    instrument_product = models.CharField(choices=INSTRUMENT_PRODUCT_TYPE,max_length=100, default="NRML")
    strategy_add_time= models.DateTimeField(auto_now_add=True,blank=True,null=True)
    sl_count_type= models.CharField(max_length=50,choices=sl_count_choices,blank=True,null=True)
    sl_value= models.FloatField(blank=True,null=True)
    candle_size_type= models.CharField(max_length=50,choices=candle_size_choices,default='POINTS',blank=True,null=True)
    trailing_sl_multiplyer = models.FloatField(null=True, blank=True)
    max_alert_candle_point = models.FloatField(null=True, blank=True)
    min_alert_candle_size = models.FloatField(default=0 , null=True, blank=True)
    stoploss_buffer = models.FloatField(null=True, blank=True)
    paper_trading = models.BooleanField(default=False)
    only_long = models.BooleanField(default=False)
    only_short = models.BooleanField(default=False)
    ignore_first_candle = models.BooleanField(default=False)
    day_high_low = models.BooleanField(default=False)
    profit_booking = models.BooleanField(default=False)
    trailing_sl = models.BooleanField(default=False)
    single_trade_mode = models.BooleanField(default=False)
    increase_qty_mode = models.BooleanField(default=False)
    option_type = models.CharField(choices=option_status, max_length=30, null=True, blank=True)
    square_off_min =  models.IntegerField(default=10, validators=[MinValueValidator(0), MaxValueValidator(30)])
    target_limit= models.IntegerField(blank=True,null=True)
    sl_limit= models.IntegerField(blank=True,null=True)
    buffer_type= models.CharField(max_length=50,choices=buffer_type_choices,blank=True,null=True)
    is_deleted=models.BooleanField(default=False)
    #need to add extra variables in it. and code chaneg accordingly