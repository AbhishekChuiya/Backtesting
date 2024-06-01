from django.db import models

# Create your models here.
class TradingInstruments(models.Model):
    instrument_token =  models.CharField(max_length=255, null=True, blank=True)
    exchange_token =  models.CharField(max_length=255, null=True, blank=True)
    tradingsymbol =  models.CharField(max_length=255, null=True, blank=True)
    name =  models.CharField(max_length=255, null=True, blank=True)
    expiry =  models.CharField(max_length=255, null=True, blank=True)
    strike =  models.FloatField(default=0.0)
    tick_size =  models.CharField(max_length=255, null=True, blank=True)
    lot_size =  models.CharField(max_length=255, null=True, blank=True)
    instrument_type =  models.CharField(max_length=255, null=True, blank=True)
    segment =  models.CharField(max_length=255, null=True, blank=True)
    exchange =  models.CharField(max_length=255, null=True, blank=True)
    name_alice = models.CharField(max_length=255, null=True, blank=True)
    instrument_token_alice = models.CharField(max_length=255, null=True, blank=True)
    segment_alice = models.CharField(max_length=255, null=True, blank=True)
    trading_symbol_alice = models.CharField(max_length=255, null=True, blank=True)
    name_angel=models.CharField(max_length=255,null=True,blank=True)
    instrument_token_angel = models.CharField(max_length=255, null=True, blank=True)
    segment_angel = models.CharField(max_length=255, null=True, blank=True)
    trading_symbol_angel = models.CharField(max_length=255, null=True, blank=True)
