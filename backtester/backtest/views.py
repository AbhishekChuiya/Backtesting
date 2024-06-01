from django.shortcuts import render
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt
from rest_framework.decorators import api_view
import pandas as pd
import numpy as np
from collections import defaultdict
from itertools import groupby
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import time
from django.core.mail import EmailMessage
from datetime import datetime as dt
import os
import sys
import plotly.graph_objects as go
from jinja2 import Template
import base64
from io import BytesIO
from PIL import Image
import requests
import pdfkit
from PIL import Image, UnidentifiedImageError
import io
from .models import BacktestResult
from wandt.models import WandTStrategy, WandTStrategyLegs


@csrf_exempt
@api_view(['POST'])
def backtest2(request):

    print(request.user)
    # wandt_strategy = WandTStrategy.objects.all()
    # print(wandt_strategy)
    # print(wandt_strategy, "wandt_strategy")
    # wandt_strategy = WandTStrategy.objects.get(user_id_id=request.user.id)
    wandt_strategies = WandTStrategy.objects.filter(user_id_id=request.user.id)

    for wandt_strategy in wandt_strategies:
        print(wandt_strategy.id)

    wandt_strategy_id = wandt_strategy.id
    print(wandt_strategy_id, "wandt_strategy_id")
    temp_var = WandTStrategyLegs.objects.filter(wandtstrategy=wandt_strategy_id)
    # temp_var = WandTStrategyLegs.objects.filter(wandtstrategy=1370)
    print(temp_var)
    print(len(temp_var))
    print(request.data, "request.data")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++")
    def generate_output(temp_var):
        output_list = []
        for obj in temp_var:
            entry_dict = {
                'broker': None,
                "is_mtom_activated": wandt_strategy.is_mtom_activated,
                "is_premium_group_calculate": wandt_strategy.is_premium_group_calculate,
                "mtom_sl_movement": wandt_strategy.mtom_sl_movement,
                "mtom_stop_loss": wandt_strategy.mtom_stop_loss,
                "mtom_target": wandt_strategy.mtom_target,
                "mtom_target_movement": wandt_strategy.mtom_target_movement,
                "mtom_trailing_sl": wandt_strategy.mtom_trailing_sl,
                "mtom_trailing_value": wandt_strategy.mtom_trailing_value,
                "paper_trading": wandt_strategy.paper_trading,
                "premium_group_exit_type": wandt_strategy.premium_group_exit_type,
                "premium_stoploss": wandt_strategy.premium_stoploss,
                "premium_target": wandt_strategy.premium_target,
                "re_entry_after_premium_exit": wandt_strategy.re_entry_after_premium_exit,
                "status": wandt_strategy.status,
                "strategy_id": wandt_strategy.strategy_id_id,
                "strategy_name": wandt_strategy.strategy_name,
                "user_id": wandt_strategy.user_id_id,
                "w_t_strategy": [
                    {
                        "action_type": obj.action_type,
                        "closest_premium_type": obj.closest_premium_type,
                        "closest_premium_value": obj.closest_premium_value,
                        "end_time": obj.end_time,
                        "exit_stop_loss": obj.exit_stop_loss,
                        "exit_target": obj.exit_target,
                        "exit_target_on": obj.exit_target_on,
                        "exit_target_type": obj.exit_target_type,
                        "expiry_days": 13,
                        "expiry_month": 12,
                        "instrument_product": obj.instrument_product,
                        "is_auto_generated": False,
                        "is_entry_grouped": obj.is_entry_grouped,
                        "is_exit_grouped": obj.is_exit_grouped,
                        "option_type": obj.option_type,
                        "qty": obj.qty,
                        "re_entry": obj.re_entry,
                        "re_entry_execute_count": 1,
                        "re_entry_execute_on_sl": obj.re_entry_execute_on_sl,
                        "re_entry_execute_on_target": obj.re_entry_execute_on_target,
                        "re_execute": obj.re_execute,
                        "selection_type": obj.selection_type,
                        "start_time": obj.start_time,
                        "strick_distance": obj.strick_distance,
                        "strick_type": obj.strick_type,
                        "target": obj.target,
                        "target_type": obj.target_type,
                        "target_up_down": obj.target_up_down,
                        "trading_instrument": obj.trading_instrument_id,
                        "trailing_sl": obj.trailing_sl,
                        "trailing_sl_movement": obj.trailing_sl_movement,
                        "trailing_sl_target_type": obj.trailing_sl_target_type,
                        "trailing_target_movement": obj.trailing_target_movement,
                        "wait_and_trade": False,
                        "wait_and_trade_strick_price": 0
                    }
                ]
            }
            output_list.append(entry_dict)
        return output_list
    import json
    # Fetch objects from the database
    # temp_var = WandTStrategyLegs.objects.filter(wandtstrategy=wandt_strategy_id)

    # Generate output using the function
    output = generate_output(temp_var)
    print(output)
    print("-------------------------------")
    # filtered_data = [item for item in output if item['w_t_strategy']]
    # output[0]['w_t_strategy'].extend(filtered_data[1]['w_t_strategy'])
    # output.pop(1)
    filtered_data = [item for item in output if item['w_t_strategy']]

# Check if there are any dictionaries with non-empty 'w_t_strategy'
    if len(filtered_data) > 1:
        # Iterate over the filtered data starting from the second item
        for item in filtered_data[1:]:
            # Extend the 'w_t_strategy' of the first item with the 'w_t_strategy' of the current item
            filtered_data[0]['w_t_strategy'].extend(item['w_t_strategy'])

        # Remove all items except the first one from the original data list
        output = [filtered_data[0]]

    # print(output, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # print(output)

    dict_payload = output[0]
    # json_payload = json.dumps(dict_payload)
    print(dict_payload)


    def first():
        data = dict_payload
        # data = request.data
        # print(data)

        # main_id = data.get('id', '')

        w_t_strategy_data = data['w_t_strategy']

        data_w_t_strategy = pd.DataFrame(w_t_strategy_data)

        main_data = {key: value for key, value in data.items() if key != 'w_t_strategy'}
        data_main = pd.DataFrame([main_data])

        data_main1=data_main.T
        data_w_t_strategy1=data_w_t_strategy.T
        data = pd.concat([data_w_t_strategy1, data_main1])
        data = data.T
        
        data1 = {
        'closest_premium_value': 'diffentry',
        'target_type': 'wnt_selectiontype',
        'target_up_down': 'inc_decwt',
        'exit_target': 'target_diff',
        'exit_stop_loss': 'sl_diff',
        'qty':'quantity',
        'strick_distance':'diffentry1',
        'mtom_target':'mtm_target_points',
        'mtom_stop_loss':'mtm_sl_points',
        'mtom_sl_movement':'mtm_sl_move',
        'closest_premium_type':'closesttype',
        'trailing_sl_target_type':'tr_selectiontype',
        'trailing_sl_movement':'sl_point',

        'trailing_target_movement':'tr_point',
        'mtom_target_movement':'mtm_y',
        'mtom_trailing_value':'mtm_x',
        'option_type' : 'optiontype',
        'action_type':'tradetype',
        'start_time': 'entrytime',
        'end_time': 'exittime',
        'selection_type':'entrytype',
        'strick_type':'moneyness',
        'trailing_sl':'trailingsl',
        'wait_and_trade':'waitntrade',
        'mtom_trailing_sl' : 'mtm_sl_trail',
        're_entry_execute_on_sl':'re_entry_sl',
        're_entry_execute_on_target':'re_entry_target'

        }

        data = data.rename(columns=data1)
        
        data = data.rename(columns=lambda x: x.replace('mtom', 'mtm'))
        
        data['target_diff'] = pd.to_numeric(data['target_diff'], errors='coerce')
        data['sl_diff'] = pd.to_numeric(data['sl_diff'], errors='coerce')

        # Initialize columns with False
        data['target_flag'] = False
        data['sl_flag'] = False
        data['mtm_target'] = False
        data['mtm_sl'] = False
        data['mtm_entry'] = False
        data['re_execute_leg'] = False
        data['re_entry_leg'] = False
        

        data['daysofweek']='0,1,2,3,4'

        data['total_premium_exit']=False
        data['total_premium_type']='POINT'
        data['total_premium_inc']=20
        data['total_premium_dec']=20

        data['sl_to_cost']=False
        data['square_off_both_leg']=False
        data['start']=False
        data['missquareoff']=True
        data['option']=False
        data['optiontrade']=False
        data['target']=0
        data['stoploss']=0
        data['startingltp']=0
        data['entrytrigger']=0
        data['tr_ltp']=0
        data['tr_target']=0
        data['trail_flag']=False
        data['straddle']=False
        data['strategy_flag']=True
        data['target_type']=None
        data['sl_type']=None
        data['re_entry_count']=0
        data['re_entry_times']=1
        data['re_execute_count']=0
        data['re_execute_times']=1


        data['profit_lock_points'] = 0
        data['mtm_lock_profit'] = False
        data['lock_trail_flag'] = False
        data['re_execute_times_sl'] = 0        
        # Conditions for target_flag and sl_flag
        data.loc[(data['target_diff'] == 10000.0) & (data['sl_diff'] == 10000.0), ['target_flag', 'sl_flag']] = False
        data.loc[(data['target_diff'] != 10000.0) & (data['sl_diff'] == 10000.0), 'target_flag'] = True
        data.loc[(data['target_diff'] == 10000.0) & (data['sl_diff'] != 10000.0), 'sl_flag'] = True
        data.loc[(data['target_diff'] != 10000.0) & (data['sl_diff'] != 10000.0), ['target_flag', 'sl_flag']] = True

        # Conditions for re_entry_leg and re_execute_leg
        # data.loc[data['re_entry']] = True
        # data.loc[data['re_execute']] = True

        for i in range(len(data)):

            if data['is_mtm_activated'][i]==True:
                data['mtm_target'][i]=True
                data['mtm_sl'][i]=True
                data['mtm_entry'][i]=True    

            if data['exit_target_type'][i]=="POINTS":
                data['target_type'][i]='POINTS'
                data['sl_type'][i]='POINTS'
            elif data['exit_target_type'][i]=="PERCENTAGE":
                data['target_type'][i]='PERCENTAGE'
                data['sl_type'][i]='PERCENTAGE'
        # Conditions for mtm_target, mtm_sl, mtm_entry
        # data.loc[data['is_mtm_activated'], ['mtm_target', 'mtm_sl', 'mtm_entry']] = True

        data = data.T
        data=data.reset_index()
        
        if 'closesttype' not in data.iloc[:, 0].values:
    # Create a new row with the values 'closest_type' and 'less' for all columns
            new_row = pd.DataFrame([['closesttype'] + ['less'] * (data.shape[1] - 1)], columns=data.columns)

            # Append the new row to the DataFrame
            data = pd.concat([data, new_row], ignore_index=True)


        if 'tr_point' not in data.iloc[:, 0].values:
            # Create a new row with the values 'closest_type' and 'less' for all columns
            new_row = pd.DataFrame([['tr_point'] + [0] * (data.shape[1] - 1)], columns=data.columns)

            # Append the new row to the DataFrame
            data = pd.concat([data, new_row], ignore_index=True)

        if 'sl_point' not in data.iloc[:, 0].values:
            # Create a new row with the values 'closest_type' and 'less' for all columns
            new_row = pd.DataFrame([['sl_point'] + [0] * (data.shape[1] - 1)], columns=data.columns)

            # Append the new row to the DataFrame
            data = pd.concat([data, new_row], ignore_index=True)
        if 'tr_selectiontype' not in data.iloc[:, 0].values:
            # Create a new row with the values 'closest_type' and 'less' for all columns
            new_row = pd.DataFrame([['tr_selectiontype'] + [0] * (data.shape[1] - 1)], columns=data.columns)

            # Append the new row to the DataFrame
            data = pd.concat([data, new_row], ignore_index=True)


        if 'diffentry' not in data.iloc[:, 0].values:
            # Create a new row with the values 'closest_type' and 'less' for all columns
            new_row = pd.DataFrame([['diffentry'] + [0] * (data.shape[1] - 1)], columns=data.columns)

            # Append the new row to the DataFrame
            data = pd.concat([data, new_row], ignore_index=True)


        if 'moneyness' not in data.iloc[:, 0].values:
            # Create a new row with the values 'closest_type' and 'less' for all columns
            new_row = pd.DataFrame([['moneyness'] + ["ATM"] * (data.shape[1] - 1)], columns=data.columns)

            # Append the new row to the DataFrame
            data = pd.concat([data, new_row], ignore_index=True)
    #     csv_path = 'files'
        print(data)
        data=data.set_index("index")
        csv_filename = f"files/nifty_legs.csv"
        # csv_filename = f"nifty_legs.csv"

    #     if os.path.exists(csv_filename):
    #         os.remove(csv_filename)
        
        # csv_file_path = os.path.join(csv_path, csv_filename)

        data.to_csv(csv_filename)
    first()

    legs=[]
    def convert_to_int_list(key, value):
        # Convert a comma-separated string of integers to a list of integers
        try:
            if ',' in value:
                # text_file.write(int_list, "before")
                int_list = [int(day.strip()) for day in value.split(',')]

            else:
                int_list = [int(day.strip()) for day in value]
                
    #         text_file.write("int_list",int_list)
            return int_list
        except ValueError:
            return value

    def read_csv_to_list_of_dicts(filename):
        df = pd.read_csv(filename, header=None, skip_blank_lines=True, dtype='object')
        for col in range(1, len(df.columns)):
            data_dict = {}
            for index, row in df.iterrows():
                if not pd.isnull(row[0]):
                    key = row[0]
                    value = row[col]
                    if pd.notna(value):
                        # Check if the value is a comma-separated list of integers
                        if key=='daysofweek':
                            value = convert_to_int_list(key, value)
                        else:
                            # Check if the value is a time format
                            if '.' in value and (key=='entrytime' or key=='exittime'):
                                # Split the time format into hours, minutes, and seconds
                                time_parts = value.split('.')
                                hours, minutes, seconds = time_parts + ['00'] * (3 - len(time_parts))
                                
                                # Add leading zeros for single-hour, single-minute, and single-second strings
                                hours = hours.zfill(2)
                                minutes = minutes.zfill(2)
                                seconds = seconds.zfill(2)
                                
                                value = f"{hours}:{minutes}:{seconds}"
                            else:
                                # Convert 'TRUE' and 'FALSE' strings to boolean values
                                if value.upper() == 'TRUE':
                                    value = True
                                elif value.upper() == 'FALSE':
                                    value = False
                                else:
                                    # Try converting to int and float df types
                                    try:
                                        value = int(value)
                                    except ValueError:
                                        try:
                                            value = float(value)
                                        except ValueError:
                                            pass
                        
                        if key in data_dict:
                            data_dict[key] = f"{data_dict[key]}, {value}"
                        else:
                            data_dict[key] = value
            
            legs.append(data_dict)
    #         text_file.write("Legs")
    #         text_file.write("Legs",legs)
        return legs

    # filename = "Input CSV/T1.csv"
    filename = "files/nifty_legs.csv"
    # filename = "files/Updated_csv.csv"
    # filename = "backtester/files/bnf_2022/Updated_csv.csv"
    # filename = []

# for kk in filename:

    leg_dicts_list = read_csv_to_list_of_dicts(filename)

    def add_unique_keys(dict_list):
        for i, d1 in enumerate(dict_list):
            for key, value in d1.items():
                for j, d2 in enumerate(dict_list):
                    if i != j and key not in d2:
                        d2[key] = value

        
    add_unique_keys(legs)

    global output_content, dayy, a12, b12, ltp_flag, temp, temp1, mtm_x, mtm_y, max_un, run_up_list, max_run_up_profit, max_run_up_loss, dict2, temp_99, cumulative_pnl, counter1, max_un_pr, max_un_ls,  total_pnl,trading_days, cummulative_trade, profit, winning_days, loss, lossing_days, winning_trades,\
                lossing_trades, winning_trades, tradepnl, SL_count, mis_count,expiry,par,\
                monday_pnl_2023,tuesday_pnl_2023,wednesday_pnl_2023, thursday_pnl_2023,friday_pnl_2023,jan_pnl_2023,feb_pnl_2023,mar_pnl_2023,apr_pnl_2023,may_pnl_2023,jun_pnl_2023,jul_pnl_2023,aug_pnl_2023,sep_pnl_2023,oct_pnl_2023,nov_pnl_2023,dec_pnl_2023, daystart, mtmslleg, max_spot, min_spot, pnl, daily_call_pnl, total_trade, target_count,\
                monday_pnl_2022,tuesday_pnl_2022,wednesday_pnl_2022, thursday_pnl_2022,friday_pnl_2022,jan_pnl_2022,feb_pnl_2022,mar_pnl_2022,apr_pnl_2022,may_pnl_2022,jun_pnl_2022,jul_pnl_2022,aug_pnl_2022,sep_pnl_2022,oct_pnl_2022,nov_pnl_2022,dec_pnl_2022,\
                monday_pnl_2021,tuesday_pnl_2021,wednesday_pnl_2021, thursday_pnl_2021,friday_pnl_2021,jan_pnl_2021,feb_pnl_2021,mar_pnl_2021,apr_pnl_2021,may_pnl_2021,jun_pnl_2021,jul_pnl_2021,aug_pnl_2021,sep_pnl_2021,oct_pnl_2021,nov_pnl_2021,dec_pnl_2021,\
                monday_pnl_2020,tuesday_pnl_2020,wednesday_pnl_2020, thursday_pnl_2020,friday_pnl_2020,jan_pnl_2020,feb_pnl_2020,mar_pnl_2020,apr_pnl_2020,may_pnl_2020,jun_pnl_2020,jul_pnl_2020,aug_pnl_2020,sep_pnl_2020,oct_pnl_2020,nov_pnl_2020,dec_pnl_2020,\
                monday_pnl_2019,tuesday_pnl_2019,wednesday_pnl_2019, thursday_pnl_2019,friday_pnl_2019,jan_pnl_2019,feb_pnl_2019,mar_pnl_2019,apr_pnl_2019,may_pnl_2019,jun_pnl_2019,jul_pnl_2019,aug_pnl_2019,sep_pnl_2019,oct_pnl_2019,nov_pnl_2019,dec_pnl_2019,\
                monday_pnl_2018,tuesday_pnl_2018,wednesday_pnl_2018, thursday_pnl_2018,friday_pnl_2018,jan_pnl_2018,feb_pnl_2018,mar_pnl_2018,apr_pnl_2018,may_pnl_2018,jun_pnl_2018,jul_pnl_2018,aug_pnl_2018,sep_pnl_2018,oct_pnl_2018,nov_pnl_2018,dec_pnl_2018
    
    total_trade=0
    max_spot=0.0
    min_spot=99999.99
    SL_count=0
    mis_count=0
    cummulative_trade=0
    lossing_trades=0
    winning_trades=0
    loss=0
    profit=0
    lossing_days=0
    winning_days=0

    total_pnl=0
    expiry_month=[]
    dailypnl=[]
    cumulative_pnl=[]
    day=[]
    datee=[]
    month=[]
    a = 0
    ####
    pnl=0
    profit=0
    loss=0
    trading_days=0

    win_strk=0
    lose_strk=0
    win_strk_t=0
    lose_strk_t=0
    pnl_perday=0
    pnl_pertrade=0
    par=[]
    res=[]
    dar=[]
    des=[]

    total_pnl=0
    dictt={}
    dict1={}
    dict2={}
    day=[]
    pnl_d=[]
    datee=[]
    daily_call_pnl=[]
    daily_put_pnl=[]
    expiry_day=[]
    trades=[]

    openspot=[]
    maxspot=[]
    minspot=[]
    winning_days=0
    lossing_days=0
    daily_trades=0
    winning_trades=0
    lossing_trades=0
    dpnl={}
    tpnl=[]
    ttrade=[]
    ttdays=[]
    pnlpd=[]
    wndays=[]
    lsdays=[]
    avgpwd=[]
    avglld=[]
    mdp=[]
    mdl=[]
    wnstk=[]
    lsstk=[]
    dwacr=[]
    tradepnl=[]

    trade_dt=[]
    trade_exp=[]
    trade_day=[]
    trade_typel=[]
    instrument=[]
    max_run_up_profit=[]
    max_run_up_loss=[]


    entry_t=[]
    exit_t=[]
    entry_p=[]
    exit_p=[]
    tttrades=[]
    pnlpt=[]
    wntrades=[]
    lstrades=[]
    avgpwt=[]
    avgllt=[]
    mtp=[]
    mtl=[]
    wnstk_t=[]
    lsstk_t=[]
    twacr=[]
    slcount=[]
    miscount=[]
    daywise_accuracy=0
    avg_profit_winning_days=0
    avg_profit_winning_trades=0
    avg_loss_lossing_trades=0
    avg_loss_lossing_days=0
    total_pnl=0
    max_spot=0.0
    min_spot=99999.99
    cummulative_trade=0
    target_count=0
    SL_count=0
    mis_count=0

    monday_pnl_2018=0
    tuesday_pnl_2018=0
    wednesday_pnl_2018=0
    thursday_pnl_2018=0
    friday_pnl_2018=0

    monday_pnl_2019=0
    tuesday_pnl_2019=0
    wednesday_pnl_2019=0
    thursday_pnl_2019=0
    friday_pnl_2019=0

    monday_pnl_2020=0
    tuesday_pnl_2020=0
    wednesday_pnl_2020=0
    thursday_pnl_2020=0
    friday_pnl_2020=0

    monday_pnl_2021=0
    tuesday_pnl_2021=0
    wednesday_pnl_2021=0
    thursday_pnl_2021=0
    friday_pnl_2021=0

    monday_pnl_2022=0
    tuesday_pnl_2022=0
    wednesday_pnl_2022=0
    thursday_pnl_2022=0
    friday_pnl_2022=0

    monday_pnl_2023=0
    tuesday_pnl_2023=0
    wednesday_pnl_2023=0
    thursday_pnl_2023=0
    friday_pnl_2023=0
    
    jan_pnl_2018=0
    feb_pnl_2018=0
    mar_pnl_2018=0
    apr_pnl_2018=0
    may_pnl_2018=0
    jun_pnl_2018=0
    jul_pnl_2018=0
    aug_pnl_2018=0
    sep_pnl_2018=0
    oct_pnl_2018=0
    nov_pnl_2018=0
    dec_pnl_2018=0

    jan_pnl_2019=0
    feb_pnl_2019=0
    mar_pnl_2019=0
    apr_pnl_2019=0
    may_pnl_2019=0
    jun_pnl_2019=0
    jul_pnl_2019=0
    aug_pnl_2019=0
    sep_pnl_2019=0
    oct_pnl_2019=0
    nov_pnl_2019=0
    dec_pnl_2019=0

    jan_pnl_2020=0
    feb_pnl_2020=0
    mar_pnl_2020=0
    apr_pnl_2020=0
    may_pnl_2020=0
    jun_pnl_2020=0
    jul_pnl_2020=0
    aug_pnl_2020=0
    sep_pnl_2020=0
    oct_pnl_2020=0
    nov_pnl_2020=0
    dec_pnl_2020=0

    jan_pnl_2021=0
    feb_pnl_2021=0
    mar_pnl_2021=0
    apr_pnl_2021=0
    may_pnl_2021=0
    jun_pnl_2021=0
    jul_pnl_2021=0
    aug_pnl_2021=0
    sep_pnl_2021=0
    oct_pnl_2021=0
    nov_pnl_2021=0
    dec_pnl_2021=0

    jan_pnl_2022=0
    feb_pnl_2022=0
    mar_pnl_2022=0
    apr_pnl_2022=0
    may_pnl_2022=0
    jun_pnl_2022=0
    jul_pnl_2022=0
    aug_pnl_2022=0
    sep_pnl_2022=0
    oct_pnl_2022=0
    nov_pnl_2022=0
    dec_pnl_2022=0
    jan_pnl_2023=0
    feb_pnl_2023=0
    mar_pnl_2023=0
    apr_pnl_2023=0
    may_pnl_2023=0
    jun_pnl_2023=0
    jul_pnl_2023=0
    aug_pnl_2023=0
    sep_pnl_2023=0
    oct_pnl_2023=0
    nov_pnl_2023=0
    dec_pnl_2023=0
    daily_pnl=0
    max_un_pr = []
    max_un_ls = []
    temp = []
    temp1 = []
    daily_ce=0
    flag1 = False
    daily_pe=0
    total_trade=0
    fix_spot=0
    daystart=False
    mtm_sl_points = legs[0]['mtm_sl_points'] 
    mtmslleg=legs[0]['mtm_sl_points']
    counter1 = 0
    per_change_max_column = []
    per_change_min_column = []
    per_change_close_column = []
    cumulative_pnl = []
    trading_days_list = []
    mtm_x = legs[0]['mtm_x']
    mtm_y = legs[0]['mtm_y']
    flag = False
    lock_sl_temp = 0

    if legs[0]['trading_instrument'] == 1:
        lot_size = 25
    elif (legs[0]['trading_instrument'] == 2) or (legs[0]['trading_instrument'] == 3):
        lot_size = 50

    a12 = pd.to_datetime('09:15:00').time()
    # a12 = pd.to_datetime('09:15:01').time()
    b12 = pd.to_datetime('15:29:30').time()
    # b12 = pd.to_datetime('15:29:59').time()
    # c = pd.to_datetime(legs[0]['entrytime']).time()
    # d = pd.to_datetime(legs[0]['exittime']).time()
    e12 = pd.to_datetime('09:15:00').time()

    a123 = pd.to_datetime('2023-05-24').date()


    date_format = "%Y-%m-%d"

    # dates_to_check = [
    #     "2020-01-31"
    # ]

    dates_to_check = [
        "2021-12-31",
        "2022-01-26", "2022-03-01", "2022-03-18", "2022-04-14", "2022-04-15", "2022-05-03",
        "2022-08-09", "2022-08-15", "2022-08-31", "2022-10-05", "2022-10-24", "2022-10-26",
        "2022-11-08", "2023-01-26", "2023-03-07", "2023-03-30", "2023-04-04", "2023-04-07",
        "2023-04-14", "2023-05-01", "2023-06-28", "2023-08-15", "2023-09-19", "2023-10-02",
        "2023-10-24", "2023-11-14", "2023-11-27", "2023-12-25", "2020-02-21", "2020-03-10",
        "2020-04-02", "2020-04-06", "2020-04-10", "2020-04-14", "2020-05-01", "2020-05-25",
        "2020-10-02", "2020-11-16", "2020-11-30", "2020-12-25", "2021-01-26", "2021-03-11",
        "2021-03-29", "2021-04-02", "2021-04-14", "2021-04-21", "2021-05-13", "2021-07-21",
        "2021-08-19", "2021-09-10", "2021-10-15", "2021-11-04", "2021-11-05", "2021-11-19",  "2020-03-11", "2020-03-12", "2020-03-09", "2022-09-30"
    ]
    dates_to_check = [pd.to_datetime(date_str).date() for date_str in dates_to_check]
    
    dates_to_check1 = [
        "2018-03-27","2018-09-11","2018-09-18","2018-10-16","2019-03-19","2019-08-13","2020-03-31","2021-03-09","2021-05-11","2021-08-17","2021-11-02","2022-04-12","2023-04-09",]
    dates_to_check1 = [pd.to_datetime(date_str1).date() for date_str1 in dates_to_check1]

    dates_to_check2 = [
            "2018-08-14","2018-05-21","2019-04-16","2019-04-30","2019-06-04","2019-10-01","2019-12-24","2021-04-13","2021-04-20","2021-07-20","2022-01-25","2022-08-30","2022-10-04","2022-10-25","2023-04-16","2023-04-30"]
    dates_to_check2 = [pd.to_datetime(date_str2).date() for date_str2 in dates_to_check2]
    
    dates_to_check3 = [
            "2018-11-05","2018-11-06"]
    dates_to_check3 = [pd.to_datetime(date_str3).date() for date_str3 in dates_to_check3]

    ltp_flag = False
    dict2={}
    temp_99=[]

    max_un=[]

    # dayy = ["Wednesday", "Thursday"]
    dayy = ["Thursday"]
    # dayy = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    run_up_list = []
    qty = legs[0]['quantity']
    #PATH
    txt_name = f"backtest/files/E.txt"
    # txt_name = f"E:/EzQuant/Data/Backtesting_data/ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_.txt"
    for leg in legs:
        leg['entrytime']=pd.to_datetime(leg['entrytime']).time()
        leg['exittime']=pd.to_datetime(leg['exittime']).time()
    with open(txt_name, "w") as text_file: 
        
        def backtest(df,prefix,start_index):
            expiry=prefix[-7:-2]
            year=prefix[-2:]
            indexoption=prefix[:-7]
            pnl = 0
            global lock_sl_temp, mtm_sl_points, mtm_x, mtm_y, ltp_flag, temp_99,dict2,lot_size,dates_to_check2,dates_to_check2,dates_to_check1,run_up_list, max_run_up_profit, max_run_up_loss, e12, flag, max_un,temp, temp1, max_un_pr, max_un_ls, qty, cumulative_pnl, per_change_max, per_change_min, per_change_close, high_spot_change, low_spot_change, close_spot_change,counter1,a12,b12,c,d,flag1, start_time, dayy, trading_days,total_trade,max_spot,min_spot,SL_count,mis_count,cummulative_trade,target_count,\
                        lossing_trades,winning_trades,loss,profit,lossing_days,winning_days,total_pnl,monday_pnl_2022,tuesday_pnl_2022,wednesday_pnl_2022,\
                        thursday_pnl_2022,friday_pnl_2022,jan_pnl_2022,feb_pnl_2022,mar_pnl_2022,apr_pnl_2022,may_pnl_2022,jun_pnl_2022,jul_pnl_2022,aug_pnl_2022,sep_pnl_2022,oct_pnl_2022,nov_pnl_2022,dec_pnl_2022,monday_pnl_2023,tuesday_pnl_2023,wednesday_pnl_2023,\
                        thursday_pnl_2023,friday_pnl_2023,jan_pnl_2023,feb_pnl_2023,mar_pnl_2023,apr_pnl_2023,may_pnl_2023,jun_pnl_2023,jul_pnl_2023,aug_pnl_2023,sep_pnl_2023,oct_pnl_2023,nov_pnl_2023,dec_pnl_2023,daystart,mtmslleg, monday_pnl_2021,tuesday_pnl_2021,wednesday_pnl_2021,thursday_pnl_2021,friday_pnl_2021,jan_pnl_2021,feb_pnl_2021,mar_pnl_2021,apr_pnl_2021,may_pnl_2021,jun_pnl_2021,jul_pnl_2021,aug_pnl_2021,sep_pnl_2021,oct_pnl_2021,nov_pnl_2021,dec_pnl_2021, monday_pnl_2020,tuesday_pnl_2020,wednesday_pnl_2020,thursday_pnl_2020,friday_pnl_2020,jan_pnl_2020,feb_pnl_2020,mar_pnl_2020,apr_pnl_2020,may_pnl_2020,jun_pnl_2020,jul_pnl_2020,aug_pnl_2020,sep_pnl_2020,oct_pnl_2020,nov_pnl_2020,dec_pnl_2020, monday_pnl_2019,tuesday_pnl_2019,wednesday_pnl_2019,thursday_pnl_2019,friday_pnl_2019,jan_pnl_2019,feb_pnl_2019,mar_pnl_2019,apr_pnl_2019,may_pnl_2019,jun_pnl_2019,jul_pnl_2019,aug_pnl_2019,sep_pnl_2019,oct_pnl_2019,nov_pnl_2019,dec_pnl_2019, monday_pnl_2018,tuesday_pnl_2018,wednesday_pnl_2018,thursday_pnl_2018,friday_pnl_2018,jan_pnl_2018,feb_pnl_2018,mar_pnl_2018,apr_pnl_2018,may_pnl_2018,jun_pnl_2018,jul_pnl_2018,aug_pnl_2018,sep_pnl_2018,oct_pnl_2018,nov_pnl_2018,dec_pnl_2018
            df['date']=pd.to_datetime(df['date'])
            for i in range(0,len(df)):

                # df['date'].iloc[i].day_name() in dayy and len(dayy) <= 5 and
                # if df['date'].iloc[i].day_name() in dayy and len(dayy) <= 5 and df.date[i].date() not in dates_to_check and not (date1 <= df.date[i].date() <= date2):
                # if (df.date[i].date() in dates_to_check1):
                #     dayy = ["Tuesday","Wednesday"]
                    
                # elif (df.date[i].date() in dates_to_check2):
                #     dayy = ["Thursday"]
                                                                            
                # elif (df.date[i].date() in dates_to_check3):
                #     dayy = ["Monday","Tuesday"]
                    
                # else:
                #     dayy = ["Wednesday","Thursday"]
                
                
                if (df['date'].iloc[i].day_name() in dayy and len(dayy) <= 5 and df.date[i].date() not in dates_to_check):
                        if df.spot[i]!=0:
                            
                            for leg in legs:
                                if df.date[i].time() > leg['entrytime'] and df.date[i].time() <b12 and leg['optiontrade']==True :
                                    
                                    if leg['optiontype']=="CE":
                                        exit1=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                        pnl1=buy_or_sell(leg['tradetype'],leg['ltp'],exit1)
                                        # text_file.write(daily_pnl, pnl1, df['date'][i].time(), "CE")
                                        # Sum1=pnl1
                                        # Sum1.append(pnl1 + daily_pnl)
                                        max_un.append(Sum1)
                                        run_up_list.append(Sum1)
                                        run_up_list.append(pnl1)
                                        max_un.append(pnl1)

                                        run_up_list.append(0)
                                        # text_file.write(run_up_list, "CE")
                                        # Sum1 = Sum1 + daily_pnl 
                                    if leg['optiontype']=="PE":
                                        exit1=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                        pnl2=buy_or_sell(leg['tradetype'],leg['ltp'],exit1)
                                        # text_file.write(daily_pnl, pnl2, df['date'][i].time(), "PE")
                                        # Sum1.append(pnl1)
                                        max_un.append(Sum1)
                                        max_un.append(pnl2)
                                        run_up_list.append(Sum1)
                                        run_up_list.append(pnl2)
                                        run_up_list.append(0)
                                        # text_file.write(run_up_list, "PE")
                                        # Sum1 = Sum1 + daily_pnl 
                                    
                                        # text_file.write(pnl1 + pnl2 + daily_pnl, df['date'][i].time())
                                    # text_file.write(Sum1, "SUM1", df['date'][i].time())
                                    
                                    Sum1 = pnl1 + pnl2 + daily_pnl
                                    max_un.append(pnl1+pnl2)
                                    max_un.append(Sum1)
                                    max_un.append(0)
                                if daystart==False and df['date'][i].time()==a12:
                                    

                                    fix_spot=df.spot[i]
                                    daystart=True
                                    min_spot=99999.9
                                    
                                    max_spot=0.0
                                    daily_pnl=0

                                    daily_ce=0

                                    daily_pe=0
                                    ltp_flag = False
                                    total_trade=0

                                    mtm_premium_target=0
                                    
                                    mtm_premium_sl=0
                                    lock_points = legs[0]['profit_lock_points']
                                    lock_sl=0
                                    profit_lock=0  
                                    trailing=False
                                    # text_file.write(df['date'].iloc[i].day_name())
                                    Sum1 = 0
                                    for leg in legs:
                                        leg['mtm_sl_points']=mtmslleg

                                    en_spot=df.spot[i]

                                    mtmtime=df['date'][i].time()
                                if leg['start']==False and df['date'][i].time() == leg['entrytime'] and leg['strategy_flag']==True:                  
                                # if leg['start']==False and df['date'][i].time() == c and df['date'][i].date().weekday() and leg['strategy_flag']==True:                  
                                    try:
                                        df.spot[i]!=0
                                    except:
                                        text_file.write("Sdsdsd")

                                    strike=int(round(df.spot[i],-2))
                                    
                                    if all(leg['start']==False for leg in legs):
                                            
                                            text_file.write('*******************************_____________________**********************************\n')
                                            text_file.write('\n')

                                            
                                            text_file.write(f"DATE: {df['date'][i].date()}, DAY: {df['date'].iloc[i].day_name()}\n")
                                            text_file.write('\n')

                                            
                                            daily_pnl=0

                                            daily_ce=0

                                            daily_pe=0
                                            Sum1 = 0
                                            total_trade=0

                                            mtm_premium_target=0
                                            
                                            mtm_premium_sl=0
                                            pnl1 = 0
                                            pnl2 = 0
                                            en_spot=df.spot[i]

                                            # fix_spot=df.spot[i]
                                            mtm_time=df['date'][i].time()
                                            
                                            day_done=False
                                    
                                    leg['strike']=entry_strike(leg['optiontype'],leg['entrytype'],leg['closesttype'],strike,leg['diffentry'],leg['moneyness'],df,i,expiry,year,indexoption)
                                    leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]

                                    text_file.write("********************************\n")
                                    # text_file.write(f"leg'ltp',{leg['ltp']}\n")

                                    leg['startingltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                    # text_file.write(leg['startingltp'])

                                    
                                    text_file.write(f"TIME: {df['date'][i].time()} -- Strike : {strike} -- Spot : {df.spot[i]}\n")

                                    text_file.write(f'{leg["strike"]}{leg["optiontype"]} = {leg["ltp"]}\n') 
                                    # text_file.write(f"{leg['ltp']}, {df.date[i].time()}")           
                                    temp.append(leg['ltp'])
                                    temp1.append(leg['ltp'])
                                    leg['optiontrade']=False
                                    
                                    leg['option']=False      
                                            
                                    
                                    if leg['waitntrade']==False:


                                        
                                        leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                        
                                        text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                        
                                        leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                        
                                        text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                        text_file.write('\n')

                                        leg['optiontrade']=True
                                        
                                        leg['option']=True

                                        entry_p.append(leg['ltp'])
                                        entry_t.append(df['date'][i].time())
                                        trade_typel.append(leg['tradetype'])
                                        instrument.append(f"{leg['strike']}{leg['optiontype']}")
                                        
                                    elif leg['waitntrade']==True:
                                        
                                        leg['entrytrigger']=waitandtrade(leg['wnt_selectiontype'],leg['inc_decwt'],leg['diff_wnt'],leg['ltp'])
                                        
                                        text_file.write(f'WNT ENTRY-TRIG: {leg["strike"]}{leg["optiontype"]} = {leg["entrytrigger"]}\n')
                                    
                                    
                                    leg['start']=True
                                    
                                    leg['missquareoff']=False

                                    leg['re_entry_count']=0
                                    
                                    leg['re_execute_count']=0
                                    leg['mtm_x'] = mtm_x
                                    leg['mtm_y'] = mtm_y
                                    
                                    leg['re_entry_leg']=False
                                    
                                    leg['mtm_entry']=False
                                    leg['lock_trail_flag']=False
                                    leg['mtm_trail_flag']=False
                                    
                                    leg['max_run_up_profit']=0
                                    leg['max_run_up_loss']=0
                                    
                                    leg['mtm_sl_points']=mtmslleg
                                    if leg['ltp'] == 0.0:
                                        day_done=False
                                        leg['optiontrade'] = False
                                    
                                        # b12 = df['date'][i].time() 
                                        # leg['exittime'] = b12
                                        ltp_flag = True

                                    total_premium_exit=0
                                    if leg['total_premium_exit']==True and all(leg['optiontrade']==True for leg in legs):
                                        for leg in legs:
                                            # if leg['optiontrade'] ==True:
                                                total_premium_exit=total_premium(leg['ltp'],leg['tradetype'],total_premium_exit)
                                        total_premium_exit_inc=total_premium_exit+leg['total_premium_inc']
                                        total_premium_exit_dec=total_premium_exit-leg['total_premium_dec']
                                        # text_file.write(f'inc pre- {total_premium_exit_inc}, dec pre- {total_premium_exit_dec}')
                                    
                                if leg['start']==True and leg['missquareoff']==False:
                                

                                    
                                    if leg['optiontrade']==True:
                                        
                                        leg['max_run_up_profit']=min(leg['max_run_up_profit'],df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i])
                                        leg['max_run_up_loss']=max(leg['max_run_up_loss'],df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i])
                                    
                                    if df['date'][i].time() == leg['exittime']:
                                        # if df['date'][i].time() == d:
                                        
                                        leg['start']=False
                                        # max_un_pr.append(max(max_un))
                                        # max_un_ls.append(min(max_un))
                                        # text_file.write(max_un_pr)
                                        # text_file.write(max_un_ls)
                                        # text_file.write(df.date[i].time())
                                        # temp = []
                                        
                                        leg['missquareoff']=True
                                        
                                        # leg['strategy_flag']=True
                                        
                                        ext_spot=df.spot[i]
                                    
                                    # if en_spot!=ext_spot:

                                        if leg['optiontrade']==True:
                                            
                                            exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                            
                                            text_file.write(f"MIS-SQUARE-OFF: {leg['strike']}{leg['optiontype']} = {exit}, Time: {df['date'][i].time()}\n")
                                            
                                            pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                            max_un.append(pnl)
                                            run_up_list.append(pnl)
                                            text_file.write(f'PNL: {pnl}\n')
                                            text_file.write('\n')

                                            total_pnl+=pnl

                                            daily_pnl+=pnl

                                            total_trade+=1
                                            trading_days_list.append(cummulative_trade)
                                            
                                            
                                            mis_count+=1

                                            if leg['optiontype']=='CE':
                                                
                                                daily_ce+=pnl

                                            else:

                                                daily_pe+=pnl

                                            if pnl>0:
                                                
                                                winning_trades+=1
                                            
                                            else:
                                                
                                                lossing_trades+=1
                                            
                                            # text_file.write(df['date'][i].time())



                                            # text_file.write(max_un_pr)
                                            # text_file.write(max_un_ls)
                                            # text_file.write(df.date[i].time())
                                            # temp = []
                                            # max_un = []
                                                
                                            tradepnl.append(pnl)
                                            
                                            
                                            leg['optiontrade']=False
                                            run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                            run_up_list.append(run_up)
                                            max_run_up_profit.append(max(run_up_list))
                                            leg['max_run_up_profit']=0
                                            
                                            run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                            run_up_list.append(run_up_loss)
                                            max_run_up_loss.append(min(run_up_list))
                                            
                                            leg['max_run_up_loss']=0
                                            
                                            trade_day.append(df['date'].iloc[i].day_name())
                                            trade_dt.append(df['date'][i].date())                        
                                            trade_exp.append(expiry)
                                            exit_p.append(exit)
                                            exit_t.append(df['date'][i].time())
                                            max_run_up_pr=max(run_up_list)
                                            max_run_up_ls=min(run_up_list)
                                            run_up_list = []
                                            dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                            temp_99.append(dict2.copy()) 

                                            
                                            # text_file.write(dict2)
                            
                                max_spot=max(max_spot,df.spot[i])
                                    
                                min_spot=min(min_spot,df.spot[i])            
                                if all(leg['missquareoff']==True for leg in legs)  and df['date'][i].time()==b12 and day_done==False or ltp_flag == True:
                                    ltp_flag = False
                                    day_done=True
                                    
                                    daystart=False
                                    for leg in legs:
                                        
                                        leg['strategy_flag']=True

                                        leg['optiontrade']=False
                                    # if en_spot==df.spot[i]:
                                        # entry_p.pop()
                                        # entry_t.pop()
                                        # trade_typel.pop()
                                        # instrument.pop()
                                
                                    # else:
                                    if daily_pnl>0:
                                        
                                        profit+=daily_pnl
                                        
                                        winning_days+=1
                                    
                                    if daily_pnl<0:
                                        
                                        loss+=daily_pnl
                                        
                                        lossing_days+=1
                                    
                                    if total_trade>0:
                                        
                                        trading_days+=1
                                    
                                        
                                    cummulative_trade+=total_trade

                                    
                                    trades.append(total_trade)
                                    
                                    expiry_day.append(expiry)                    
                                    
                                    par.append(daily_pnl)
                                    
                                    pnl_d.append(daily_pnl)
                                    # text_file.write(pnl_d,  df['date'][i].time())
                                    cumulative_pnl.append(total_pnl)

                                                
                                    closespot=df.spot[i]
                                    if fix_spot != 0:
                                        per_change_close=float(format(100*((closespot-fix_spot)/fix_spot),'.2f'))
                                        
                                        per_change_max=float(format(100*((max_spot-fix_spot)/fix_spot),'.2f'))
                                        
                                        per_change_min=float(format(100*((min_spot-fix_spot)/fix_spot),'.2f'))

                        
                                    else:
                                        text_file.write("Error: fix_spot is zero. Division by zero not allowed.\n")

                                        # per_change_close = 0
                                        # per_change_max = 0
                                        # per_change_min = 0
                                    
                                        # text_file.write("Exception")
                                        
                                    maxspot.append(f'{max_spot}({per_change_max})')
                                    
                                    minspot.append(f'{min_spot}({per_change_min})')
                                    
                                    openspot.append(fix_spot) 
                                    # changehere
                                    counter1 += 1
                                    print(counter1, df['date'][i].date())   
                                    
                                    text_file.write(f'CE PNL : {daily_ce}\n')            
                                    
                                    text_file.write(f'PE PNL : {daily_pe}\n')
                                    
                                    text_file.write(f'Daily PNL : {daily_pnl}\n')
                                    
                                    text_file.write(f'Total PNL : {total_pnl}\n')
                                    text_file.write('\n')
                                    
                                    per_change_max_column.append(per_change_max)
                                    per_change_min_column.append(per_change_min)
                                    per_change_close_column.append(per_change_close)
                                    # text_file.write(df.date[i].time())
                                    # max_un_pr.append(max(max_un))
                                    # max_un_ls.append(min(max_un))
                                    # # text_file.write(max_un_pr)
                                    # # text_file.write(max_un_ls)
                                    # # text_file.write(df.date[i].time())
                                    max_un.append(0)
                                    max_un_pr.append(max(max_un))
                                    max_un_ls.append(min(max_un))
                                    # text_file.write(max_un_pr, "max_un_pr")
                                    # text_file.write(max_un_ls, "max_un_ls")
                                    # text_file.write(max_run_up_profit)
                                    # text_file.write(max_run_up_loss)
                                    temp = []
                                    temp1 = []
                                    Sum1 = 0
                                    max_un = []
                                    run_up_list = []
                                    # max_un_pr = []
                                    # max_un_ls = []
                                    # max_run_up_profit=[]
                                    # max_run_up_loss=[]
                                    
                                    leg['trail_flag']=False
                                    leg['re_execute_leg'] = False
                                    if leg['trading_instrument'] == 1:
                                        text_file.write(f'BNF OPEN :{fix_spot}, HIGH : {max_spot} ({per_change_max}), LOW :{min_spot} ({per_change_min}), CLOSE :{closespot} ({per_change_close})\n')
                                    elif leg['trading_instrument'] == 2:
                                        text_file.write(f'NF OPEN :{fix_spot}, HIGH : {max_spot} ({per_change_max}), LOW :{min_spot} ({per_change_min}), CLOSE :{closespot} ({per_change_close})\n')
                                    elif leg['trading_instrument'] == 3:
                                        text_file.write(f'FNF OPEN :{fix_spot}, HIGH : {max_spot} ({per_change_max}), LOW :{min_spot} ({per_change_min}), CLOSE :{closespot} ({per_change_close})\n')
                                    text_file.write('****************************************************************************************************************\n')
                                    text_file.write('\n')

                                    min_spot=99999.9
                                    
                                    max_spot=0.0
                                    
                                    dailypnl.append(daily_pnl)
                                    
                                    expiry_month.append(expiry)
                                    
                                    day.append(df['date'].iloc[i].day_name())
                                    
                                    datee.append(df['date'][i].date())
                                    
                                    month.append((df['date'][i].date()).strftime('%B'))
                                    
                                    #for monthly calculations
                                    
                                    if (df['date'][i].date()).strftime('%B')=='January':
                                        if year == "18":
                                            jan_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            jan_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            jan_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            jan_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            jan_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            jan_pnl_2023+=daily_pnl
                                    
                                    elif (df['date'][i].date()).strftime('%B')=='February':
                                        if year == "18":
                                            feb_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            feb_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            feb_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            feb_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            feb_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            feb_pnl_2023+=daily_pnl                        

                                    elif (df['date'][i].date()).strftime('%B')=='March':
                                        if year == "18":
                                            mar_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            mar_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            mar_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            mar_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            mar_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            mar_pnl_2023+=daily_pnl

                                    elif (df['date'][i].date()).strftime('%B')=='April':
                                        if year == "18":
                                            apr_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            apr_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            apr_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            apr_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            apr_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            apr_pnl_2023+=daily_pnl

                                    elif (df['date'][i].date()).strftime('%B')=='May':
                                        if year == "18":
                                            may_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            may_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            may_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            may_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            may_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            may_pnl_2023+=daily_pnl


                                    elif (df['date'][i].date()).strftime('%B')=='June':
                                        if year == "18":
                                            jun_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            jun_pnl_2019+=daily_pnl
                                        elif year == "19":
                                            jun_pnl_2020+=daily_pnl
                                        elif year == "20":
                                            jun_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            jun_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            jun_pnl_2023+=daily_pnl

                                    elif (df['date'][i].date()).strftime('%B')=='July':
                                        if year == "18":
                                            jul_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            jul_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            jul_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            jul_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            jul_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            jul_pnl_2023+=daily_pnl

                                    elif (df['date'][i].date()).strftime('%B')=='August':
                                        if year == "18":
                                            aug_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            aug_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            aug_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            aug_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            aug_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            aug_pnl_2023+=daily_pnl

                                    elif (df['date'][i].date()).strftime('%B')=='September':
                                        if year == "18":
                                            sep_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            sep_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            sep_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            sep_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            sep_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            sep_pnl_2023+=daily_pnl

                                    elif (df['date'][i].date()).strftime('%B')=='October':
                                        if year == "18":
                                            oct_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            oct_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            oct_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            oct_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            oct_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            oct_pnl_2023+=daily_pnl

                                    elif (df['date'][i].date()).strftime('%B')=='November':
                                        if year == "18":
                                            nov_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            nov_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            nov_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            nov_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            nov_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            nov_pnl_2023+=daily_pnl

                                    elif (df['date'][i].date()).strftime('%B')=='December':
                                        if year == "18":
                                            dec_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            dec_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            dec_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            dec_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            dec_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            dec_pnl_2023+=daily_pnl

                                    #for weekdays calculations

                                    if df['date'].iloc[i].day_name()=='Monday':
                                        if year == "18":
                                            monday_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            monday_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            monday_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            monday_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            monday_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            monday_pnl_2023+=daily_pnl
                                    
                                    if df['date'].iloc[i].day_name()=='Tuesday':
                                        if year == "18":
                                            tuesday_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            tuesday_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            tuesday_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            tuesday_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            tuesday_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            tuesday_pnl_2023+=daily_pnl
                                        
                                    
                                    if df['date'].iloc[i].day_name()=='Wednesday':
                                        if year == "18":
                                            wednesday_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            wednesday_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            wednesday_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            wednesday_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            wednesday_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            wednesday_pnl_2023+=daily_pnl

                                    
                                    if df['date'].iloc[i].day_name()=='Thursday':
                                        if year == "18":
                                            thursday_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            thursday_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            thursday_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            thursday_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            thursday_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            thursday_pnl_2023+=daily_pnl

                                    if df['date'].iloc[i].day_name()=='Friday':
                                        if year == "18":
                                            friday_pnl_2018+=daily_pnl
                                        elif year == "19":
                                            friday_pnl_2019+=daily_pnl
                                        elif year == "20":
                                            friday_pnl_2020+=daily_pnl
                                        elif year == "21":
                                            friday_pnl_2021+=daily_pnl
                                        elif year == "22":
                                            friday_pnl_2022+=daily_pnl
                                        elif year == "23":
                                            friday_pnl_2023+=daily_pnl                                        
                                            
                                if leg['start']==True and leg['missquareoff']==False and leg['optiontrade']==True and (leg['mtm_sl']==True or leg['mtm_target']==True or leg['mtm_sl_trail']==True  or leg['mtm_lock_profit']==True) and mtmtime!=df['date'][i].time():
                                    if mtmtime!=df['date'][i].time():
                                        mtm_premium_sl=0
                                        mtm_premium_target=0                    
                                        
                                        mtmtime=df['date'][i].time()
                                        mtm_premium_sl+=daily_pnl
                                        mtm_premium_target+=daily_pnl
                                        for leg in legs:
                                            
                                            if leg['optiontrade']==True:
                                                exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                
                                                pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                max_un.append(pnl)
                                                run_up_list.append(pnl)
                                                mtm_premium_sl+=pnl
                                                mtm_premium_target+=pnl


                                    if Sum1 +lock_points<lock_points and  leg['mtm_lock_profit']==True and  leg['lock_trail_flag']==False:
                                        profit_lock=0
                                        profit_lock=Sum1 +lock_points
                                        
                                    #changehere
                                    if Sum1 +lock_points>lock_points and leg['mtm_lock_profit']==True and  leg['lock_trail_flag']==False: 
                                        leg['lock_trail_flag']=True
                                        trailing=False
                                        profit_lock=Sum1 +leg['profit_lock_points']
                                        print("profit_lock start",profit_lock,df.date[i].time(),leg['ltp'])
                                        print(Sum1)
                                    
                                        
                                    #changehere
                                    if leg['lock_trail_flag']==True and Sum1>profit_lock and  trailing==False:
                                        lock_sl=16
                                        global lock_sl_temp
                                        lock_sl_temp = 16
                                        profit_lock+=leg['lock_x_points'] 
                                        profit_lock+=leg['lock_x_points'] 
                                        print("lock_sl",lock_sl)
                                        print("Time",df.date[i].time())
                                        trailing=True
                                            
                                    if leg['lock_trail_flag']==True and trailing==True:
                                        # text_file.write("PNL",pnl_leg1 + pnl_leg2 + daily_pnl)
                                        # text_file.write(lock_sl)
                                        
                                        while (Sum1)>profit_lock:
                                            
                                        
                                            
                                            # text_file.write(df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i],leg['stoploss'],leg['optiontrade'],leg['tradetype'],leg['sl_flag'])
                                            
                                            profit_lock+=leg['lock_x_points']
                                            lock_sl+=leg['lock_y_points']
                                            #changehere
                                            print("profit_lock",profit_lock)
                                            print("Sum1",Sum1)
                                            print("lock_sl",lock_sl)
                                            print("Time",df.date[i].time())
                                            
                                            # text_file.write("Time",df.date[i].time())
                                            
                                            # text_file.write("PNL",pnl_leg1 + pnl_leg2 + daily_pnl,daily_pnl)
                                    #changehere
                                    if leg['lock_trail_flag']==True and trailing==True and Sum1<lock_sl:
                                        trailing=False
                                        day_done=True
                                        daystart=False
                                        print("sl hit")
                                        print("Sum1",Sum1)
                                        print("lock_sl",lock_sl)
                                        lock_sl=0
                                        profit_lock=0  
                                        print("Time",df.date[i].time())
                                        # text_file.write("PNL",pnl_leg1 + pnl_leg2 + daily_pnl)
                                        for leg in legs:
                                            leg['lock_trail_flag']=False 
                                            # leg['mtm_lock_profit']=False
                                            # leg['missquareoff']=False
                                            leg['trailingsl']=False
                                            leg['start']=False
                                        # max_un_pr.append(max(max_un))
                                        # max_un_ls.append(min(max_un))
                                        # text_file.write(max_un_pr)
                                        # text_file.write(max_un_ls)
                                        # text_file.write(df.date[i].time())
                                        # temp = []
                                        
                                            leg['missquareoff']=True
                                            if leg['optiontrade']==True:
                                                leg['optiontrade']=False
                                                exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                
                                                text_file.write(f"LOCK-SQUARE-OFF: {leg['strike']}{leg['optiontype']} = {exit}, Time: {df['date'][i].time()}\n")
                                                
                                                pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                max_un.append(pnl)
                                                run_up_list.append(pnl)
                                                
                                                text_file.write(f'PNL: {pnl}\n')
                                                text_file.write('\n')

                                                total_pnl+=pnl

                                                daily_pnl+=pnl
                                                
                                                total_trade+=1
                                                trading_days_list.append(cummulative_trade)
                                                
                                                
                                                mis_count+=1

                                                if leg['optiontype']=='CE':
                                                    
                                                    daily_ce+=pnl

                                                else:

                                                    daily_pe+=pnl

                                                if pnl>0:
                                                    
                                                    winning_trades+=1
                                                
                                                else:
                                                    
                                                    lossing_trades+=1
                                                
                                                # text_file.write(df['date'][i].time())



                                                # text_file.write(max_un_pr)
                                                # text_file.write(max_un_ls)
                                                # text_file.write(df.date[i].time())
                                                # temp = []
                                                # max_un = []
                                                    
                                                tradepnl.append(pnl)

                                                leg['optiontrade']=False
                                                run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                                max_run_up_profit.append(run_up)
                                                leg['max_run_up_profit']=0
                                                
                                                run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                                max_run_up_loss.append(run_up_loss)
                                                leg['max_run_up_loss']=0
                                                
                                                trade_day.append(df['date'].iloc[i].day_name())
                                                trade_dt.append(df['date'][i].date())                        
                                                trade_exp.append(expiry)
                                                exit_p.append(exit)
                                                exit_t.append(df['date'][i].time())
                                                # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                                # text_file.write(dict2)
                                                max_run_up_pr=max(max_run_up_profit)
                                                max_run_up_ls=min(max_run_up_loss)
                                                run_up_list = []
                                                dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                                temp_99.append(dict2.copy()) 

                                                
                                        lock_sl=0
                                        profit_lock=0        
                                        max_spot=max(max_spot,df.spot[i])
                                            
                                        min_spot=min(min_spot,df.spot[i])            
                                        
                                        for leg in legs:
                                            
                                            leg['strategy_flag']=True

                                            leg['optiontrade']=False
                                        # if en_spot==df.spot[i]:
                                            # entry_p.pop()
                                            # entry_t.pop()
                                            # trade_typel.pop()
                                            # instrument.pop()
                                    
                                    # else:
                                        if daily_pnl>0:
                                            
                                            profit+=daily_pnl
                                            
                                            winning_days+=1
                                        
                                        if daily_pnl<0:
                                            
                                            loss+=daily_pnl
                                            
                                            lossing_days+=1
                                        
                                        if total_trade>0:
                                            
                                            trading_days+=1
                                        
                                            
                                        cummulative_trade+=total_trade

                                        
                                        trades.append(total_trade)
                                        
                                        expiry_day.append(expiry)                    
                                        
                                        par.append(daily_pnl)
                                        
                                        pnl_d.append(daily_pnl)
                                        cumulative_pnl.append(total_pnl)

                                                        
                                        closespot=df.spot[i]
                                        if fix_spot != 0:
                                            per_change_close=float(format(100*((closespot-fix_spot)/fix_spot),'.2f'))
                                            
                                            per_change_max=float(format(100*((max_spot-fix_spot)/fix_spot),'.2f'))
                                            
                                            per_change_min=float(format(100*((min_spot-fix_spot)/fix_spot),'.2f'))

                            
                                        else:
                                            text_file.write("Error: fix_spot is zero. Division by zero not allowed.\n")

                                            # per_change_close = 0
                                            # per_change_max = 0
                                            # per_change_min = 0
                                        
                                            # text_file.write("Exception")
                                            
                                        maxspot.append(f'{max_spot}({per_change_max})')
                                        
                                        minspot.append(f'{min_spot}({per_change_min})')
                                        
                                        openspot.append(fix_spot) 
                                        #changehere
                                        counter1 += 1
                                        print(counter1, df['date'][i].date())   
                                        
                                        text_file.write(f'CE PNL : {daily_ce}\n')            
                                        
                                        text_file.write(f'PE PNL : {daily_pe}\n')
                                        
                                        text_file.write(f'Daily PNL : {daily_pnl}\n')
                                        
                                        text_file.write(f'Total PNL : {total_pnl}\n')
                                        text_file.write('\n')
                                        
                                        per_change_max_column.append(per_change_max)
                                        per_change_min_column.append(per_change_min)
                                        per_change_close_column.append(per_change_close)
                                        # text_file.write(df.date[i].time())
                                        max_un_pr.append(max(max_un))
                                        max_un_ls.append(min(max_un))
                                        datee.append(df['date'][i].date())
                                        # # text_file.write(max_un_pr)
                                        # # text_file.write(max_un_ls)
                                        # # text_file.write(df.date[i].time())
                                        pnl_leg1=0
                                        Sum1=0
                                        pnl_leg2=0
                                        # max_un_pr.append(max(max_un))
                                        # max_un_ls.append(min(max_un))
                                        temp = []
                                        temp1 = []
                                        max_un = []
                                        leg['trail_flag']=False
                                        leg['re_execute_leg'] = False
                                        if leg['trading_instrument'] == 1:
                                            text_file.write(f'BNF OPEN :{fix_spot}, HIGH : {max_spot} ({per_change_max}), LOW :{min_spot} ({per_change_min}), CLOSE :{closespot} ({per_change_close})\n')
                                        elif leg['trading_instrument'] == 2:
                                            text_file.write(f'NF OPEN :{fix_spot}, HIGH : {max_spot} ({per_change_max}), LOW :{min_spot} ({per_change_min}), CLOSE :{closespot} ({per_change_close})\n')
                                        elif leg['trading_instrument'] == 3:
                                            text_file.write(f'FNF OPEN :{fix_spot}, HIGH : {max_spot} ({per_change_max}), LOW :{min_spot} ({per_change_min}), CLOSE :{closespot} ({per_change_close})\n')
                                        text_file.write('****************************************************************************************************************\n')
                                        text_file.write('\n')
                                    
                                    if leg['mtm_sl_trail']==True:
                                        if mtm_premium_target>leg['mtm_x'] and leg['mtm_trail_flag']==False:
                                            text_file.write(f"{leg['mtm_x']}\n")
                                            text_file.write(f'MTM TARGET LTP PR {mtm_premium_target}, MTMX {leg["mtm_x"]}, {df.date[i]}\n')
                                            for leg in legs:
                                                leg['mtm_trail_flag']=True
                                                leg['mtm_x']=mtm_premium_target + leg['mtm_y']
                                                
                                        if mtm_premium_target>leg['mtm_x'] and leg['mtm_trail_flag']==True:
                                            text_file.write(f'MTM TARGET LTP PR {mtm_premium_target}, MTMX {leg["mtm_x"]}, {df.date[i]}\n')
                                            
                                            while mtm_premium_target>leg['mtm_x']:
                                                for leg in legs:
                                                    leg['mtm_x']+=leg['mtm_y']
                                                    leg['mtm_sl_points']+=leg['mtm_sl_move']
                                            text_file.write(f'SL MOVED TO {leg["mtm_sl_points"]}\n')
                                                    
                                    if leg['mtm_sl']==True:
                                        
                                        
                                        
                                        leg['mtm_entry']=True

                                        if (mtm_premium_sl*lot_size)<=leg['mtm_sl_points']:

                                            # text_file.write(f'MTM-STOPLOSS: {mtm_premium_sl*lot_size }')
                                            
                                            text_file.write(f"{pnl}\n")
                                            
                                            for leg in legs:
                                                leg['strategy_flag']=False
                                                if leg['optiontrade']==True:
                                                    
                                                    exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                    
                                                    text_file.write(f'MTM-STOPLOSS LEG-SQUARE-OFF: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME: {df["date"][i].time()}')
                                                    
                                                    pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                    
                                                    max_un.append(pnl)
                                                    run_up_list.append(pnl)
                                                    
                                                    text_file.write(f'PNL {pnl}\n')
                                                    
                                                    total_pnl+=pnl
                                                    daily_pnl+=pnl

                                                    total_trade+=1
                                                    trading_days_list.append(cummulative_trade)
                                                    
                                                    SL_count+=1

                                                    if leg['optiontype']=='CE':
                                                        
                                                        daily_ce+=pnl
                                                    else:

                                                        daily_pe+=pnl
                                                    
                                                    if pnl>0:
                                                            
                                                        winning_trades+=1
                                                    
                                                    else:
                                                        
                                                        lossing_trades+=1
                                                    
                                                    tradepnl.append(pnl)
                                                    
                                                    mtm_premium_sl=0                                   
                                                    
                                                    
                                                    
                                                    run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                                    run_up_list.append(run_up)
                                                    max_run_up_profit.append(max(run_up_list))
                                                    leg['max_run_up_profit']=0
                                                    
                                                    run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                                    run_up_list.append(run_up_loss)
                                                    
                                                    max_run_up_loss.append(min(run_up_list))
                                                    
                                                    leg['max_run_up_loss']=0

                                                    leg['optiontrade']=False
                                                    trade_day.append(df['date'].iloc[i].day_name())
                                                    trade_dt.append(df['date'][i].date())                        
                                                    trade_exp.append(expiry)
                                                    exit_p.append(exit)
                                                    exit_t.append(df['date'][i].time())
                                                    max_run_up_pr=max(run_up_list)
                                                    max_run_up_ls=min(run_up_list)
                                                    run_up_list = []
                                                    dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                                    temp_99.append(dict2.copy()) 

                                    
                                    if leg['mtm_target']==True:
                                        # leg['mtm_entry']=True
                                        
                                        if (mtm_premium_target*lot_size)>=leg['mtm_target_points']:
                                            
                                            text_file.write(f'MTM-TARGET: {mtm_premium_target*lot_size}')
                                            
                                            for leg in legs:
                                                leg['strategy_flag']=False
                                                
                                                if leg['optiontrade']==True:
                                                    
                                                    exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                    
                                                    text_file.write(f'MTM-TARGET LEG-SQUARE-OFF: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME: {df["date"][i].time()}')
                                                    
                                                    pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                    max_un.append(pnl)
                                                    run_up_list.append(pnl)
                                                    
                                                    text_file.write(f'PNL {pnl}\n')
                                                    
                                                    total_pnl+=pnl

                                                    daily_pnl+=pnl

                                                    total_trade+=1
                                                    trading_days_list.append(cummulative_trade)
                                                    
                                                    target_count+=1

                                                    if leg['optiontype']=='CE':
                                                        
                                                        daily_ce+=pnl
                                                    else:

                                                        daily_pe+=pnl
                                                    
                                                    if pnl>0:
                                                            
                                                        winning_trades+=1
                                                    
                                                    else:
                                                        
                                                        lossing_trades+=1
                                                    
                                                    tradepnl.append(pnl)
                                                    
                                                    mtm_premium_target=0

                                                    leg['optiontrade']=False
                                                    
                                                    
                                                    run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                                    run_up_list.append(run_up)
                                                    
                                                    max_run_up_profit.append(max(run_up_list))
                                                    leg['max_run_up_profit']=0

                                                    run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                                    run_up_list.append(run_up_loss)
                                                    max_run_up_loss.append(min(run_up_list))
                                                    
                                                    leg['max_run_up_loss']=0

                                                    trade_day.append(df['date'].iloc[i].day_name())
                                                    trade_dt.append(df['date'][i].date())                        
                                                    trade_exp.append(expiry)
                                                    exit_p.append(exit)
                                                    exit_t.append(df['date'][i].time())
                                                    # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                                    # text_file.write(dict2)
                                                    max_run_up_pr=max(run_up_list)
                                                    max_run_up_ls=min(run_up_list)
                                                    run_up_list = []
                                                    dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                                    temp_99.append(dict2.copy()) 

                                
                                if leg['start']==True and leg['missquareoff']==False :                
                                    prem_ex=False
                                    if leg['total_premium_exit']==True and all(leg['optiontrade']==True for leg in legs) and prem_ex==False:
                                        total_premium_exit=0
                                        prem_ex=True
                                        for leg in legs:
                                            if leg['optiontrade'] ==True:
                                                # text_file.write(f'strike {leg["strike"]}, option {leg["optiontype"]}, trade {leg["tradetype"]}, ',df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i])
                                                total_premium_exit=total_premium(df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i],leg['tradetype'],total_premium_exit)
                                        if total_premium_exit>total_premium_exit_inc:
                                            text_file.write(f'{total_premium_exit} > {total_premium_exit_inc} {df.date[i]}\n')
                                            for leg in legs:
                                                
                                                if leg['optiontrade']==True:
                                                    
                                                    exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                    
                                                    text_file.write(f'LEG-SQUARE-OFF: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME: {df["date"][i].time()}\n')
                                                    
                                                    pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                    max_un.append(pnl)
                                                    run_up_list.append(pnl)
                                                    
                                                    text_file.write(f'the pnl is {pnl}\n')
                                                    
                                                    leg['optiontrade']=False
                                                    
                                                    total_pnl+=pnl

                                                    daily_pnl+=pnl

                                                    total_trade+=1
                                                    trading_days_list.append(cummulative_trade)

                                                    if leg['optiontype']=='CE':
                                                        
                                                        daily_ce+=pnl
                                                    else:

                                                        daily_pe+=pnl
                                                    
                                                    if pnl>0:
                                                            
                                                        winning_trades+=1
                                                    
                                                    else:
                                                        
                                                        lossing_trades+=1
                                                    
                                                    tradepnl.append(pnl)
                                                    
                                                    leg['optiontrade']=False
                                                    
                                                    trade_day.append(df['date'].iloc[i].day_name())
                                                    trade_dt.append(df['date'][i].date())                        
                                                    trade_exp.append(expiry)
                                                    exit_p.append(exit)
                                                    exit_t.append(df['date'][i].time())

                                                    run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                                    run_up_list.append(run_up)
                                                    max_run_up_profit.append(max(run_up_list))
                                                    leg['max_run_up_profit']=0

                                                    run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                                    run_up_list.append(run_up_loss)
                                                    max_run_up_loss.append(min(run_up_list))
                                                    
                                                    leg['max_run_up_loss']=0
                                                    # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                                    max_run_up_pr=max(run_up_list)
                                                    max_run_up_ls=min(run_up_list)
                                                    run_up_list = []
                                                    dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                                    temp_99.append(dict2.copy()) 

                                    

                                        if total_premium_exit<total_premium_exit_dec:
                                            text_file.write(f'{total_premium_exit} < {total_premium_exit_dec} {df.date[i]}\n')
                                            for leg in legs:
                                                
                                                if leg['optiontrade']==True:
                                                    
                                                    exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                    
                                                    text_file.write(f'LEG-SQUARE-OFF: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME: {df["date"][i].time()}\n')
                                                    
                                                    pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                    max_un.append(pnl)
                                                    run_up_list.append(pnl)
                                                    
                                                    text_file.write(f'the pnl is {pnl}\n')
                                                    
                                                    leg['optiontrade']=False
                                                    
                                                    total_pnl+=pnl

                                                    daily_pnl+=pnl

                                                    total_trade+=1
                                                    trading_days_list.append(cummulative_trade)

                                                    if leg['optiontype']=='CE':
                                                        
                                                        daily_ce+=pnl
                                                    else:

                                                        daily_pe+=pnl
                                                    
                                                    if pnl>0:
                                                            
                                                        winning_trades+=1
                                                    
                                                    else:
                                                        
                                                        lossing_trades+=1
                                                    
                                                    tradepnl.append(pnl)
                                                    

                                                    leg['optiontrade']=False
                                                    
                                                    trade_day.append(df['date'].iloc[i].day_name())
                                                    trade_dt.append(df['date'][i].date())                        
                                                    trade_exp.append(expiry)
                                                    exit_p.append(exit)
                                                    exit_t.append(df['date'][i].time())

                                                    run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                                    run_up_list.append(run_up)
                                                    max_run_up_profit.append(max(run_up_list))
                                                    leg['max_run_up_profit']=0

                                                    run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                                    run_up_list.append(run_up_loss)
                                                    max_run_up_loss.append(min(run_up_list))
                                                    
                                                    leg['max_run_up_loss']=0
                                                    max_run_up_pr=max(run_up_list)
                                                    max_run_up_ls=min(run_up_list)
                                                    run_up_list = []
                                                    dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                                    temp_99.append(dict2.copy()) 

                                    
                                                    # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                                    
                                    prem_ex=False
                                    
                                    if leg['trailingsl']==True:
                                        
                                        leg['tr_ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        # text_file.write( f"{leg['trailingsl']}, {leg['optiontrade']}, TRAIL FLAG {leg['trail_flag']}, {df.date[i].time()}, STRIKE {leg['strike']}, TR LTP {leg['tr_ltp']}")
                                        if leg['optiontrade']==True:
                                            
                                            leg['stoploss'],leg['tr_target'],leg['trail_flag']=trail_sl(leg['tr_selectiontype'],leg['tradetype'],leg['tr_ltp'],leg['stoploss'],leg['tr_point'],leg['sl_point'],df,i,leg['strike'],expiry,leg['optiontype'],leg['tr_target'],leg['trail_flag'])

                                    #without wnt
                                    #selling
                                    if df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]<leg['target'] and leg['optiontrade']==True and leg['tradetype']=='SELL' and leg['target_flag']==True:                    
                                        
                                        exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                        text_file.write(f'TARGET HIT: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME: {df["date"][i].time()}\n')
                                        
                                        pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                        max_un.append(pnl)
                                        run_up_list.append(pnl)
                                        
                                        text_file.write(f'PNL: {pnl}\n')              
                                        
                                        total_pnl+=pnl

                                        daily_pnl+=pnl

                                        total_trade+=1
                                        trading_days_list.append(cummulative_trade)

                                        target_count+=1

                                        if leg['optiontype']=='CE':
                                            
                                            daily_ce+=pnl
                                        else:

                                            daily_pe+=pnl
                                        
                                        if pnl>0:
                                                
                                            winning_trades+=1
                                        
                                        else:
                                            
                                            lossing_trades+=1
                                        
                                        tradepnl.append(pnl)
                                        
                                        trade_day.append(df['date'].iloc[i].day_name())
                                        trade_dt.append(df['date'][i].date())                        
                                        trade_exp.append(expiry)
                                        exit_p.append(exit)
                                        exit_t.append(df['date'][i].time())
                                        
                                        run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                        run_up_list.append(run_up)
                                        max_run_up_profit.append(max(run_up_list))
                                        leg['max_run_up_profit']=0

                                        run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                        run_up_list.append(run_up_loss)
                                        max_run_up_loss.append(min(run_up_list))
                                        leg['max_run_up_loss']=0

                                        leg['optiontrade']=False
                                        # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                        max_run_up_pr=max(run_up_list)
                                        max_run_up_ls=min(run_up_list)
                                        run_up_list = []
                                        
                                        dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                        temp_99.append(dict2.copy()) 

                                    

                                        if leg['square_off_both_leg']==True:                        
                                            
                                            for leg in legs:
                                                
                                                if leg['optiontrade']==True:
                                                    
                                                    exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                    
                                                    text_file.write(f'LEG-SQUARE-OFF: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME - {df["date"][i].time()}\n')
                                                    
                                                    pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                    max_un.append(pnl)
                                                    run_up_list.append(pnl)
                                                    
                                                    text_file.write(f'PNL {pnl}\n')
                                                    
                                                    total_pnl+=pnl


                                                    daily_pnl+=pnl

                                                    total_trade+=1
                                                    trading_days_list.append(cummulative_trade)

                                                    if leg['optiontype']=='CE':
                                                        
                                                        daily_ce+=pnl
                                                    else:

                                                        daily_pe+=pnl
                                                    
                                                    if pnl>0:
                                                            
                                                        winning_trades+=1
                                                    
                                                    else:
                                                        
                                                        lossing_trades+=1
                                                    
                                                    tradepnl.append(pnl)
                                                    

                                                    leg['optiontrade']=False
                                                    
                                                    trade_day.append(df['date'].iloc[i].day_name())
                                                    trade_dt.append(df['date'][i].date())                        
                                                    trade_exp.append(expiry)
                                                    exit_p.append(exit)
                                                    exit_t.append(df['date'][i].time())
                                                    
                                                    run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                                    run_up_list.append(run_up)
                                                    max_run_up_profit.append(max(run_up_list))
                                                    leg['max_run_up_profit']=0

                                                    run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                                    run_up_list.append(run_up_loss)
                                                    max_run_up_loss.append(min(run_up_list))
                                                    max_run_up_pr=max(run_up_list)
                                                    max_run_up_ls=min(run_up_list)
                                                    run_up_list = []
                                                    leg['max_run_up_loss']=0
                                                    # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                                    
                                                    dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                                    temp_99.append(dict2.copy()) 

                                    

                                            if leg['re_entry_target']==True:
                                            
                                                leg['re_entry_leg']=True
                                        
                                    if df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]>leg['stoploss'] and leg['optiontrade']==True and leg['tradetype']=='SELL' and leg['sl_flag']==True:
                                        
                                        exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                        text_file.write(f'SL HIT: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME {df["date"][i].time()}\n')
                                        
                                        pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                        max_un.append(pnl)
                                        run_up_list.append(pnl)
                                        
                                        text_file.write(f'PNL: {pnl}\n')
                                        text_file.write('\n')
                                        
                                        total_pnl+=pnl

                                        daily_pnl+=pnl

                                        total_trade+=1
                                        trading_days_list.append(cummulative_trade)

                                        if leg['optiontype']=='CE':
                                            
                                            daily_ce+=pnl
                                        else:

                                            daily_pe+=pnl
                                        
                                        if pnl>0:
                                                
                                            winning_trades+=1
                                        
                                        else:
                                            
                                            lossing_trades+=1
                                        
                                        tradepnl.append(pnl)
                                        

                                        leg['optiontrade']=False

                                        SL_count+=1
                                        
                                        trade_day.append(df['date'].iloc[i].day_name())
                                        trade_dt.append(df['date'][i].date())                        
                                        trade_exp.append(expiry)
                                        exit_p.append(exit)
                                        exit_t.append(df['date'][i].time())
                                        run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                        run_up_list.append(run_up)
                                        max_run_up_profit.append(max(run_up_list))
                                        leg['max_run_up_profit']=0

                                        run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                        run_up_list.append(run_up_loss)
                                        max_run_up_loss.append(min(run_up_list))
                                        max_run_up_pr=max(run_up_list)
                                        max_run_up_ls=min(run_up_list)
                                        run_up_list = []
                                        leg['max_run_up_loss']=0
                                        # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                        
                                        dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                        temp_99.append(dict2.copy()) 

                                    

                                        
                                        if leg['square_off_both_leg']==True:                        
                                            
                                            for leg in legs:
                                                
                                                if leg['optiontrade']==True:
                                                    
                                                    exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                    
                                                    text_file.write(f'LEG-SQUARE-OFF: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME: {df["date"][i].time()}')
                                                    
                                                    pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                    max_un.append(pnl)
                                                    run_up_list.append(pnl)
                                                    
                                                    text_file.write(f'the pnl is {pnl}\n')
                                                    
                                                    leg['optiontrade']=False
                                                    
                                                    total_pnl+=pnl

                                                    daily_pnl+=pnl

                                                    total_trade+=1
                                                    trading_days_list.append(cummulative_trade)

                                                    if leg['optiontype']=='CE':
                                                        
                                                        daily_ce+=pnl
                                                    else:

                                                        daily_pe+=pnl
                                                    
                                                    if pnl>0:
                                                            
                                                        winning_trades+=1
                                                    
                                                    else:
                                                        
                                                        lossing_trades+=1
                                                    
                                                    tradepnl.append(pnl)
                                                    

                                                    leg['optiontrade']=False
                                                    
                                                    trade_day.append(df['date'].iloc[i].day_name())
                                                    trade_dt.append(df['date'][i].date())                        
                                                    trade_exp.append(expiry)
                                                    exit_p.append(exit)
                                                    exit_t.append(df['date'][i].time())

                                                    run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                                    run_up_list.append(run_up)
                                                    max_run_up_profit.append(max(run_up_list))
                                                    leg['max_run_up_profit']=0

                                                    run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                                    run_up_list.append(run_up_loss)
                                                    max_run_up_loss.append(min(run_up_list))
                                                    
                                                    leg['max_run_up_loss']=0
                                                    max_run_up_pr=max(run_up_list)
                                                    max_run_up_ls=min(run_up_list)
                                                    run_up_list = []
                                                    dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                                    temp_99.append(dict2.copy()) 

                                    
                                                    # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                                    
                                        
                                        
                                        if leg['sl_to_cost']==True:
                                            
                                            for leg in legs:
                                                
                                                if leg['optiontrade']==True:
                                                    
                                                    leg['stoploss']=leg['ltp']
                                                    
                                                    text_file.write(f'SL TRAIL :{leg["strike"]}{leg["optiontype"]} = {leg["ltp"]}, TIME {df["date"][i].time()}\n')
                                                    text_file.write('\n')
                                        if leg['re_entry_sl']==True:
                                            
                                            leg['re_entry_leg']=True

                                        if leg['re_execute_leg']==False:
                                            
                                            leg['re_execute_leg']=True
                                    
                                    #buying
                                    
                                    if df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]>leg['target'] and leg['optiontrade']==True and leg['tradetype']=='BUY' and leg['target_flag']==True:                    
                                        
                                        exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                        text_file.write(f'TARGET HIT: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME {df["date"][i].time()}\n')
                                        
                                        pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                        max_un.append(pnl)
                                        run_up_list.append(pnl)
                                        
                                        text_file.write(f'PNL: {pnl}\n')
                                        text_file.write('\n')
                                        
                                        leg['optiontrade']=False
                                        
                                        total_pnl+=pnl

                                        daily_pnl+=pnl

                                        total_trade+=1
                                        trading_days_list.append(cummulative_trade)

                                        target_count+=1

                                        if leg['optiontype']=='CE':
                                            
                                            daily_ce+=pnl
                                        else:

                                            daily_pe+=pnl
                                        
                                        if pnl>0:
                                                
                                            winning_trades+=1
                                        
                                        else:
                                            
                                            lossing_trades+=1
                                        
                                        tradepnl.append(pnl)
                                        

                                        leg['optiontrade']=False
                                        
                                        trade_day.append(df['date'].iloc[i].day_name())
                                        trade_dt.append(df['date'][i].date())                        
                                        trade_exp.append(expiry)
                                        exit_p.append(exit)
                                        exit_t.append(df['date'][i].time())
                                        run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                        run_up_list.append(run_up)
                                        max_run_up_profit.append(max(run_up_list))
                                        leg['max_run_up_profit']=0

                                        run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                        run_up_list.append(run_up_loss)
                                        max_run_up_loss.append(min(run_up_list))
                                        
                                        leg['max_run_up_loss']=0
                                        max_run_up_pr=max(run_up_list)
                                        max_run_up_ls=min(run_up_list)
                                        run_up_list = []
                                        dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                        temp_99.append(dict2.copy()) 

                                    
                                        # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                        
                                        
                                        if leg['square_off_both_leg']==True:                        
                                            
                                            for leg in legs:
                                                
                                                if leg['optiontrade']==True:
                                                    
                                                    exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                    
                                                    text_file.write(f'LEG-SQUARE-OFF: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME: {df["date"][i].time()}\n')
                                                    
                                                    pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                    max_un.append(pnl)
                                                    run_up_list.append(pnl)
                                                    
                                                    text_file.write(f'PNL: {pnl}\n')
                                                    text_file.write('\n')
                                                    
                                                    total_pnl+=pnl

                                                    daily_pnl+=pnl

                                                    total_trade+=1
                                                    trading_days_list.append(cummulative_trade)

                                                    if leg['optiontype']=='CE':
                                                        
                                                        daily_ce+=pnl
                                                    else:

                                                        daily_pe+=pnl
                                                    
                                                    if pnl>0:
                                                            
                                                        winning_trades+=1
                                                    
                                                    else:
                                                        
                                                        lossing_trades+=1
                                                    
                                                    tradepnl.append(pnl)
                                                    

                                                    leg['optiontrade']=False
                                                    
                                                    trade_day.append(df['date'].iloc[i].day_name())
                                                    trade_dt.append(df['date'][i].date())                        
                                                    trade_exp.append(expiry)
                                                    exit_p.append(exit)
                                                    exit_t.append(df['date'][i].time())
                                                    
                                                    run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                                    run_up_list.append(run_up)
                                                    max_run_up_profit.append(max(run_up_list))
                                                    leg['max_run_up_profit']=0

                                                    run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                                    run_up_list.append(run_up_loss)
                                                    max_run_up_loss.append(min(run_up_list))
                                                    
                                                    leg['max_run_up_loss']=0      
                                                    # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                                    max_run_up_pr=max(run_up_list)
                                                    max_run_up_ls=min(run_up_list)
                                                    run_up_list = []
                                                    dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                                    temp_99.append(dict2.copy()) 


                                    if df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]<leg['stoploss'] and leg['optiontrade']==True and leg['tradetype']=='BUY' and leg['sl_flag']==True:
                                        
                                        exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                        text_file.write(f'SL HIT: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME {df["date"][i].time()}\n')
                                        
                                        pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                        max_un.append(pnl)
                                        run_up_list.append(pnl)
                                        
                                        text_file.write(f'PNL: {pnl}\n')
                                        text_file.write('\n')
                                        
                                        total_pnl+=pnl

                                        daily_pnl+=pnl

                                        total_trade+=1
                                        trading_days_list.append(cummulative_trade)

                                        if leg['optiontype']=='CE':
                                            
                                            daily_ce+=pnl
                                        else:

                                            daily_pe+=pnl
                                        
                                        if pnl>0:
                                                
                                            winning_trades+=1
                                        
                                        else:
                                            
                                            lossing_trades+=1
                                            
                                            SL_count+=1
                                            
                                        
                                        tradepnl.append(pnl)
                                        

                                        leg['optiontrade']=False

                                        
                                        trade_day.append(df['date'].iloc[i].day_name())
                                        trade_dt.append(df['date'][i].date())                        
                                        trade_exp.append(expiry)
                                        exit_p.append(exit)
                                        exit_t.append(df['date'][i].time())
                                        
                                        run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                        # text_file.write(run_up)
                                        run_up_list.append(run_up)
                                        max_run_up_profit.append(max(run_up_list))
                                        leg['max_run_up_profit']=0

                                        run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                        run_up_list.append(run_up_loss)
                                        max_run_up_loss.append(min(run_up_list))
                                        
                                        leg['max_run_up_loss']=0
                                        max_run_up_pr=max(run_up_list)
                                        max_run_up_ls=min(run_up_list)
                                        run_up_list = []
                                        dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                        temp_99.append(dict2.copy()) 

                                    
                                        # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                        

                                        if leg['square_off_both_leg']==True:                        
                                            
                                            for leg in legs:
                                                
                                                if leg['optiontrade']==True:
                                                
                                                    exit=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                                    
                                                    text_file.write(f'LEG-SQUARE-OFF: {leg["strike"]}{leg["optiontype"]} = {exit}, TIME {df["date"][i].time()}\n')
                                                    
                                                    pnl=buy_or_sell(leg['tradetype'],leg['ltp'],exit)
                                                    max_un.append(pnl)
                                                    run_up_list.append(pnl)
                                                    
                                                    text_file.write(f' {pnl}\n')
                                                    text_file.write('\n')
                                                    
                                                    total_pnl+=pnl

                                                    daily_pnl+=pnl

                                                    total_trade+=1
                                                    trading_days_list.append(cummulative_trade)

                                                    if leg['optiontype']=='CE':
                                                        
                                                        daily_ce+=pnl
                                                    else:

                                                        daily_pe+=pnl
                                                    
                                                    if pnl>0:
                                                            
                                                        winning_trades+=1
                                                    
                                                    else:
                                                        
                                                        lossing_trades+=1
                                                    
                                                    tradepnl.append(pnl)
                                                    

                                                    leg['optiontrade']=False
                                                    
                                                    trade_day.append(df['date'].iloc[i].day_name())
                                                    trade_dt.append(df['date'][i].date())                        
                                                    trade_exp.append(expiry)
                                                    exit_p.append(exit)
                                                    exit_t.append(df['date'][i].time())
                                                    
                                                    run_up=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_profit'])
                                                    run_up_list.append(run_up)
                                                    max_run_up_profit.append(max(run_up_list))
                                                    leg['max_run_up_profit']=0

                                                    run_up_loss=buy_or_sell(leg['tradetype'],leg['ltp'],leg['max_run_up_loss'])
                                                    run_up_list.append(run_up_loss)
                                                    max_run_up_loss.append(min(run_up_list))
                                                    
                                                    leg['max_run_up_loss']=0
                                                    max_run_up_pr=max(run_up_list)
                                                    max_run_up_ls=min(run_up_list)
                                                    run_up_list = []
                                                    
                                                    dict2.update({"Day" : df['date'].iloc[i].day_name(),"Date" : df['date'][i].date(),"Expiry" : expiry,"Trade Type" : leg['tradetype'],"Instrument" : f"{leg['strike']}{leg['optiontype']}","Entry Premium" : leg['ltp'],"Exit Time" : df['date'][i].time(),"Exit Premium" : exit,"PNL" : float(format(pnl, '.2f')), "Max unrealised Profit during whole trade" : float(format(max_run_up_pr, '.2f')),"Max unrealised loss during whole trade" : float(format(max_run_up_ls, '.2f'))})
                                                    temp_99.append(dict2.copy()) 

                                    
                                                    # dict2.update({"Instrument" : leg['strike'],"Entry Time" : leg['entrytime'],"Exit Time" : leg['exittime'],"Exit Premium" : exit,"PNL" : pnl, "Max unrealised Profit during whole trade" : max_run_up_profit,"Max unrealised loss during whole trade" : max_run_up_loss})
                                                    

                                        
                                        if leg['sl_to_cost']==True:
                                            
                                            for leg in legs:
                                                
                                                if leg['optiontrade']==True:
                                                    
                                                    leg['stoploss']=leg['ltp']

                                                    text_file.write(f'SL TRAIL :{leg["strike"]}{leg["optiontype"]} = {leg["ltp"]}, TIME {df["date"][i].time()}\n')
                                        
                                        if leg['re_entry_sl']==True:
                                            leg['re_entry_leg']=True
                                    
                                    #with wnt
                                    
                                    if leg['waitntrade']==True and df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]>leg['entrytrigger'] and leg['optiontrade']==False and leg['option']==False :
                                        
                                        leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]                    
                                        
                                        leg['startingltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                        leg['trail_flag']=False
                                        
                                        
                                        text_file.write(f'WAITNTRADE ENTRY: {leg["strike"]}{leg["optiontype"]} = {leg["ltp"]}, TIME {df["date"][i].time()}\n') 
                                        
                                        leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                    
                                        text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                        text_file.write('\n')
                                        entry_p.append(leg['ltp'])
                                        entry_t.append(df['date'][i].time())
                                        trade_typel.append(leg['tradetype'])
                                        instrument.append(f"{leg['strike']}{leg['optiontype']}")
                                        
                                        if leg['straddle']==True:
                                        
                                            leg['stoploss'],leg['spot']=stoploss(leg['startingltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                            text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                        
                                        else:
                                            leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                            text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                        
                                        leg['optiontrade']=True
                                        
                                        leg['option']=True

                                        if leg['straddle']==True:

                                            for leg in legs:
                                                
                                                if leg['option']==False:

                                                    leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]                       
                                                    
                                                    text_file.write(f'WAITNTRADE ENTRY: {leg["strike"]}{leg["optiontype"]} = {leg["ltp"]}, TIME {df["date"][i].time()}\n') 
                                                    
                                                    leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                                
                                                    text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                                    
                                                    leg['stoploss'],leg['spot']=stoploss(leg['startingltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                                    text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                                    
                                                    leg['optiontrade']=True
                                                    
                                                    leg['option']=True

                                    # if leg['waitntrade']==True and df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]>leg['entrytrigger'] and leg['optiontrade']==False and leg['option']==False :
                                        
                                    #     leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]                    
                                        
                                    #     leg['startingltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                        
                                    #     text_file.write(f'WAITNTRADE ENTRY: {leg["strike"]}{leg["optiontype"]} = {leg["ltp"]}, TIME {df["date"][i].time()}\n') 
                                        
                                    #     leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                    
                                    #     text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                    #     text_file.write('\n')
                                    #     entry_p.append(leg['ltp'])
                                    #     entry_t.append(df['date'][i].time())
                                    #     trade_typel.append(leg['tradetype'])
                                    #     instrument.append(f"{leg['strike']}{leg['optiontype']}")
                                        
                                    #     if leg['straddle']==True:
                                        
                                    #         leg['stoploss'],leg['spot']=stoploss(leg['startingltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                    #         text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                        
                                    #     else:
                                    #         leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                    #         text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                        
                                    #     leg['optiontrade']=True
                                        
                                    #     leg['option']=True

                                    #     if leg['straddle']==True:

                                    #         for leg in legs:
                                                
                                    #             if leg['option']==False:

                                    #                 leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]                       
                                                    
                                    #                 text_file.write(f'WAITNTRADE ENTRY: {leg["strike"]}{leg["optiontype"]} = {leg["ltp"]}, TIME {df["date"][i].time()}\n') 
                                                    
                                    #                 leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                                
                                    #                 text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                                    
                                    #                 leg['stoploss'],leg['spot']=stoploss(leg['startingltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                    #                 text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                                    
                                    #                 leg['optiontrade']=True
                                                    
                                    #                 leg['option']=True

                                                    
                                    #reentry
                                    
                                    if leg['optiontrade']==False and leg['option']==True and leg['re_entry']==True and  leg['re_entry_count']<leg['re_entry_times'] and leg['re_entry_leg']==True:
                                        
                                        if df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]>leg['startingltp'] and leg['re_entry_sl']==True and leg['tradetype']=='BUY': 
                                        
                                                                            
                                            leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]

                                            leg['startingltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                            
                                            # text_file.write(f"RE-ENTRY:  {leg['strike']}{leg['optiontype']} = ",leg['ltp'],f', TIME {df["date"][i].time()}\n')     
                                            text_file.write(f"RE-ENTRY: {leg['strike']}{leg['optiontype']} = {leg['ltp']}, TIME {df['date'][i].time()}\n")

                                            if leg['optiontype'] == "PE":
                                                temp1[1] = leg['ltp']
                                            if leg['optiontype'] == "CE":
                                                temp = []
                                                temp.append(leg['ltp'])
                                            leg['re_entry_count']+=1
                                            
                                            # leg['option']=False
                                            
                                            # if leg['waitntrade']==False:                    
                                            
                                            leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                            
                                            text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                            
                                            leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                            text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                            text_file.write('\n')
                                            leg['optiontrade']=True
                                            
                                            leg['option']=True
                                            
                                            entry_p.append(leg['ltp'])
                                            entry_t.append(df['date'][i].time())
                                            trade_typel.append(leg['tradetype'])
                                            instrument.append(f"{leg['strike']}{leg['optiontype']}")
                                            # elif leg['waitntrade']==True:
                                                
                                            #     leg['entrytrigger']=waitandtrade(leg['wnt_selectiontype'],leg['inc_decwt'],leg['diff_wnt'],leg['ltp'])
                                                
                                            #     text_file.write(f'WNT ENTRY-TRIG: {leg["strike"]}{leg["optiontype"]} = {leg["entrytrigger"]}\n')

                                        if df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]<leg['startingltp'] and leg['re_entry_target']==True and leg['tradetype']=='BUY': 
                                        
                                            leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]

                                            leg['startingltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                            
                                            text_file.write(f"RE-ENTRY:  {leg['strike']}{leg['optiontype']} ",leg['ltp'],f', TIME {df["date"][i].time()}\n')       
                                            if leg['optiontype'] == "PE":
                                                temp1[1] = leg['ltp']
                                            if leg['optiontype'] == "CE":
                                                temp = []
                                                temp.append(leg['ltp'])
                                            
                                            
                                            leg['re_entry_count']+=1
                                            
                                            # leg['option']=False
                                            
                                            # if leg['waitntrade']==False:                    
                                            
                                            leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                            
                                            text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                            
                                            leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                            text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                            text_file.write('\n')
                                            leg['optiontrade']=True
                                            
                                            leg['option']=True
                                            entry_p.append(leg['ltp'])
                                            entry_t.append(df['date'][i].time())
                                            trade_typel.append(leg['tradetype'])
                                            instrument.append(f"{leg['strike']}{leg['optiontype']}")
                                            
                                            # elif leg['waitntrade']==True:
                                                
                                            #     leg['entrytrigger']=waitandtrade(leg['wnt_selectiontype'],leg['inc_decwt'],leg['diff_wnt'],leg['ltp'])
                                                
                                            #     text_file.write(f'WNT ENTRY-TRIG: {leg["strike"]}{leg["optiontype"]} = {leg["entrytrigger"]}\n')
                                            
                                        if df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]>leg['startingltp'] and leg['re_entry_target']==True and leg['tradetype']=='SELL': 
                                        
                                            leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]

                                            leg['startingltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                            
                                            text_file.write(f"RE-ENTRY:  {leg['strike']}{leg['optiontype']} = ",leg['ltp'],f', TIME {df["date"][i].time()}\n')      
                                            text_file.write(leg['optiontype'], "PE3")  
                                            if leg['optiontype'] == "PE":
                                                temp1[1] = leg['ltp']
                                            if leg['optiontype'] == "CE":
                                                temp = []
                                                temp.append(leg['ltp'])
                                            
                                            leg['re_entry_count']+=1
                                            
                                            # leg['option']=False
                                            
                                            # if leg['waitntrade']==False:                    
                                            
                                            leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                            
                                            text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                            
                                            leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                            text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                            text_file.write('\n')
                                            leg['optiontrade']=True
                                            
                                            leg['option']=True
                                            
                                            entry_p.append(leg['ltp'])
                                            entry_t.append(df['date'][i].time())
                                            trade_typel.append(leg['tradetype'])
                                            instrument.append(f"{leg['strike']}{leg['optiontype']}")
                                            # elif leg['waitntrade']==True:
                                                
                                            #     leg['entrytrigger']=waitandtrade(leg['wnt_selectiontype'],leg['inc_decwt'],leg['diff_wnt'],leg['ltp'])
                                                
                                            #     text_file.write(f'WNT ENTRY-TRIG: {leg["strike"]}{leg["optiontype"]} = {leg["entrytrigger"]}\n')
                                        
                                        if df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]<leg['startingltp'] and leg['re_entry_sl']==True and leg['tradetype']=='SELL': 
                                            
                                            
                                            leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]

                                            leg['startingltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                            
                                            text_file.write(f"RE-ENTRY:  {leg['strike']}{leg['optiontype']} = {leg['ltp']}, TIME {df['date'][i].time()}\n")         
                                            # text_file.write(leg['optiontype'], "*****************************")  
                                            if leg['optiontype'] == "PE":
                                                temp1[1] = leg['ltp']
                                            if leg['optiontype'] == "CE":
                                                temp = []
                                                temp.append(leg['ltp'])
                                                                            
                                            leg['re_entry_count']+=1
                                            
                                            # leg['option']=False
                                            
                                            # if leg['waitntrade']==False:                    s
                                            
                                            leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                            
                                            text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                            
                                            leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                            text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                            text_file.write('\n')
                                            leg['optiontrade']=True
                                            
                                            leg['option']=True
                                            
                                            entry_p.append(leg['ltp'])
                                            entry_t.append(df['date'][i].time())
                                            trade_typel.append(leg['tradetype'])
                                            instrument.append(f"{leg['strike']}{leg['optiontype']}")

                                            

                                            # elif leg['waitntrade']==True:
                                                
                                            #     leg['entrytrigger']=waitandtrade(leg['wnt_selectiontype'],leg['inc_decwt'],leg['diff_wnt'],leg['ltp'])
                                                
                                            #     text_file.write(f'WNT ENTRY-TRIG: {leg["strike"]}{leg["optiontype"]} = {leg["entrytrigger"]}\n')
                                        
                                    #reexecute

                                    


                                    if leg['re_execute_count']<leg['re_execute_times'] and leg['optiontrade']==False and leg['option']==True and leg['re_execute']==True:
                                        
                                        strike=int(round(df.spot[i],-2))
                                        
                                        text_file.write(f'RE-EXECUTE -- Time {df["date"][i].time()} -- Strike : {strike} -- Spot : {df.spot[i]}\n')
                                        
                                        leg['strike']=entry_strike(leg['optiontype'],leg['entrytype'],leg['closesttype'],strike,leg['diffentry'],leg['moneyness'],df,i,expiry,year,indexoption)
                                        
                                        leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]

                                        leg['startingltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                        leg['re_execute_count']+=1

                                        # leg['trail_flag']=False
                                        
                                        leg['option']=False
                                        
                                        if leg['waitntrade']==False:           
                                            
                                            leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                            
                                            text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                            
                                            leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                            text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                            text_file.write('\n')
                                            leg['optiontrade']=True
                                            
                                            leg['option']=True
                                            
                                            entry_p.append(leg['ltp'])
                                            entry_t.append(df['date'][i].time())
                                            trade_typel.append(leg['tradetype'])
                                            instrument.append(f"{leg['strike']}{leg['optiontype']}")

                                        elif leg['waitntrade']==True:
                                            
                                            leg['entrytrigger']=waitandtrade(leg['wnt_selectiontype'],leg['inc_decwt'],leg['diff_wnt'],leg['ltp'])
                                            
                                            text_file.write(f'WNT ENTRY-TRIG: {leg["strike"]}{leg["optiontype"]} = {leg["entrytrigger"]}\n')

                                    # if leg['re_execute_count']<leg['re_execute_times_sl'] and leg['optiontrade']==False and leg['option']==True and leg['re_execute']==True and  leg['re_execute_leg']==True:
                                        
                                    #     strike=int(round(df.spot[i],-2))
                                        
                                        
                                    #     leg['strike']=entry_strike(leg['optiontype'],leg['entrytype'],leg['closesttype'],strike,leg['diffentry'],leg['moneyness'],df,i,expiry,year,indexoption)
                                        
                                    #     leg['ltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                    #     text_file.write(f'RE-EXECUTE -- Time {df["date"][i].time()} -- Strike : {strike} -- LTP : {leg['ltp']}-- Spot : {df.spot[i]}\n')


                                    #     leg['startingltp']=df[f"{indexoption}{expiry}{year}{leg['strike']}{leg['optiontype']}"][i]
                                        
                                    #     leg['re_execute_count']+=1
                                        
                                    #     leg['option']=False
                                        
                                    #     if leg['waitntrade']==False:           
                                            
                                    #         leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                            
                                    #         text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                            
                                    #         leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                    #         text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                    #         text_file.write('\n')
                                    #         leg['optiontrade']=True
                                            
                                    #         leg['option']=True
                                            
                                    #         entry_p.append(leg['ltp'])
                                    #         entry_t.append(df['date'][i].time())
                                    #         trade_typel.append(leg['tradetype'])
                                    #         instrument.append(f"{leg['strike']}{leg['optiontype']}")

                                    #     if leg['waitntrade']==True and leg['re_execute_leg']==True:

                                    #         leg['re_execute_leg']=False
                                    #         leg['target']=target_point(leg['ltp'],leg['target_type'],leg['target_diff'],leg['tradetype'],leg['target_flag'])
                                            
                                    #         text_file.write(f'TARGET: {leg["strike"]}{leg["optiontype"]} = {leg["target"]}\n')
                                            
                                    #         leg['stoploss'],leg['spot']=stoploss(leg['ltp'],df.spot[i],leg['sl_type'],leg['sl_diff'],leg['tradetype'],leg['sl_flag'])
                                            
                                    #         text_file.write(f'STOPLOSS: {leg["strike"]}{leg["optiontype"]} = {leg["stoploss"]} \n')
                                    #         text_file.write('\n')
                                    #         leg['optiontrade']=True
                                            
                                    #         leg['option']=True
                                            
                                    #         entry_p.append(leg['ltp'])
                                    #         entry_t.append(df['date'][i].time())
                                    #         trade_typel.append(leg['tradetype'])
                                    #         instrument.append(f"{leg['strike']}{leg['optiontype']}")
                        else:
                            pass
                    # if date1 != 1 and df['date'][i].date() > date2 and date2 != 1:
                    #     flag = True

                # if (date1 <= df.date[i].date() <= date2) and df.date[i].date() not in dates_to_check:
                    
            return total_pnl,trading_days, cummulative_trade, profit, winning_days, loss, lossing_days, winning_trades,\
                    lossing_trades, winning_trades, tradepnl, SL_count, mis_count,expiry,par,monday_pnl_2022,tuesday_pnl_2022,wednesday_pnl_2022,\
                    thursday_pnl_2022,friday_pnl_2022,jan_pnl_2022,feb_pnl_2022,mar_pnl_2022,apr_pnl_2022,may_pnl_2022,jun_pnl_2022,jul_pnl_2022,aug_pnl_2022,sep_pnl_2022,oct_pnl_2022,nov_pnl_2022,dec_pnl_2022,monday_pnl_2023,tuesday_pnl_2023,wednesday_pnl_2023,\
                    thursday_pnl_2023,friday_pnl_2023,jan_pnl_2023,feb_pnl_2023,mar_pnl_2023,apr_pnl_2023,may_pnl_2023,jun_pnl_2023,jul_pnl_2023,aug_pnl_2023,sep_pnl_2023,oct_pnl_2023,nov_pnl_2023,dec_pnl_2023,monday_pnl_2021,tuesday_pnl_2021,wednesday_pnl_2021,thursday_pnl_2021,friday_pnl_2021,jan_pnl_2021,feb_pnl_2021,mar_pnl_2021,apr_pnl_2021,may_pnl_2021,jun_pnl_2021,jul_pnl_2021,aug_pnl_2021,sep_pnl_2021,oct_pnl_2021,nov_pnl_2021,dec_pnl_2021, monday_pnl_2020,tuesday_pnl_2020,wednesday_pnl_2020,thursday_pnl_2020,friday_pnl_2020,jan_pnl_2020,feb_pnl_2020,mar_pnl_2020,apr_pnl_2020,may_pnl_2020,jun_pnl_2020,jul_pnl_2020,aug_pnl_2020,sep_pnl_2020,oct_pnl_2020,nov_pnl_2020,dec_pnl_2020, monday_pnl_2019,tuesday_pnl_2019,wednesday_pnl_2019,thursday_pnl_2019,friday_pnl_2019,jan_pnl_2019,feb_pnl_2019,mar_pnl_2019,apr_pnl_2019,may_pnl_2019,jun_pnl_2019,jul_pnl_2019,aug_pnl_2019,sep_pnl_2019,oct_pnl_2019,nov_pnl_2019,dec_pnl_2019, monday_pnl_2018,tuesday_pnl_2018,wednesday_pnl_2018,thursday_pnl_2018,friday_pnl_2018,jan_pnl_2018,feb_pnl_2018,mar_pnl_2018,apr_pnl_2018,may_pnl_2018,jun_pnl_2018,jul_pnl_2018,aug_pnl_2018,sep_pnl_2018,oct_pnl_2018,nov_pnl_2018,dec_pnl_2018

        def total_premium(ltp,tradetype,total_pr_exit):
            if tradetype=='SELL':
                total_pr_exit+=ltp
            if tradetype=='BUY':
                total_pr_exit+=(ltp*-1)
            return total_pr_exit

        def waitandtrade(selectiontype,value,diff,premium):   
            
            if value=='UP':        
                
                if selectiontype=='POINTS':
                
                    premium=premium+diff                
                
                elif selectiontype=='PERCENTAGE':
                    
                    premium=premium*((100+diff)/100)                
            
            if value=='DOWN':
                
                if selectiontype=='POINTS':
                    
                    premium=premium-diff                
                
                elif selectiontype=='PERCENTAGE':
                    
                    premium=premium*((100-diff)/100)                
                
            return premium

        def trail_sl(selectiontype,trade,ltp,sl,tr_point,sl_point,df,i,strike,expiry,option,tr_target,trailflag):
                
            
            if selectiontype=='POINTS':
                
                if trade=='SELL':
                    
                    if trailflag==False:
                        
                        tr_target=ltp-tr_point 
                    # premium=tr_target
                    
                    trailflag=True
                    
                    tr_stoploss=sl
                        # text_file.write(df.date[i][-8:],round(tr_stoploss_ce,2),round(ltp,2),round(tr_target_ce,2),'\n')
                                
                    if ltp<tr_target:
                        
        #                 text_file.write(df.date[i][-8:],round(tr_stoploss,2),round(ltp,2),round(tr_target,2),'\n')
                        
                        while(ltp<tr_target):
                            
                            tr_target-=tr_point
                            
                            tr_stoploss-=sl_point
                            # premium=tr_target
        #                     text_file.write(df.date[i][-8:],round(tr_stoploss,2),round(ltp,2),round(tr_target,2),'\n')
                
                if trade=='BUY':
                    
                    if trailflag==False:
                        
                        tr_target=ltp+tr_point
                    # premium=tr_target
                
                    trailflag=True
                    
                    tr_stoploss=sl
                    # text_file.write(df.date[i][-8:],round(tr_stoploss_ce,2),round(ltp,2),round(tr_target_ce,2),'\n')                                          
                    
                    if ltp>tr_target:
                        # text_file.write(df.date[i][-8:],round(tr_stoploss_ce,2),round(ltp,2),round(tr_target_ce,2),'\n')
                        
                        while(ltp>tr_target):
                            
                            tr_target+=tr_point
                            
                            tr_stoploss+=sl_point
                            # premium=tr_target
                            text_file.write(f"{df.date[i].time()},SL - {round(tr_stoploss,2)}, LTP - {round(ltp,2)}, target -  {round(tr_target,2)}\n")
            
            elif selectiontype=='PERCENTAGE':
                
                if trade=='SELL':
                    
                    if trailflag==False:            
                        
                        tr_target=ltp*((100-tr_point)/100)  
                    
                    trailflag=True            
                    
                    tr_stoploss=sl                
                    
                    if ltp<tr_target:
                        
                        # text_file.write(df.date[i][-8:],round(tr_stoploss,2),round(ltp,2),round(tr_target,2),f'{option}\n')
                        
                        while(ltp<tr_target):
                            
                            tr_target-=ltp*tr_point/100
                            
                            tr_stoploss-=ltp*sl_point/100                    
                            # premium=tr_target   
                            # text_file.write(df.date[i][-8:],round(tr_stoploss,2),round(ltp,2),round(tr_target,2),f'{option}\n')             
                
                if trade=='BUY':
                    
                    if trailflag==False:
                        tr_target=ltp*((100+tr_point)/100)                 
                    trailflag=True                
                    tr_stoploss=sl
                    if ltp>tr_target:        
        #                 text_file.write(df.date[i][-8:],round(tr_stoploss,2),round(ltp,2),round(tr_target,2),f'{option}\n')

                        while(ltp>tr_target):       
                            tr_target+=ltp*tr_point/100
                            tr_stoploss+=ltp*sl_point/100
        #                     text_file.write(df.date[i][-8:],round(tr_stoploss,2),round(ltp,2),round(tr_target,2),f'{option}\n')
                            
                            # text_file.write(df.date[i][-8:],round(tr_stoploss_ce,2),round(ltp_ce,2),round(tr_target_ce,2),'\n')              
                                    
            return tr_stoploss,tr_target,trailflag  
        #target function                   
        def target_point(premium,type,diff,trade_type,target_flag):    
            if target_flag==True:
                if trade_type=='BUY':
                    if type=='POINTS':
                        premium=premium+diff               

                    elif type=='PERCENTAGE':
                        premium=premium*((100+diff)/100)
                        
                elif trade_type=='SELL':
                    if type=='POINTS':
                        premium=premium-diff
                        
                    elif type=='PERCENTAGE':
                        premium=premium*((100-diff)/100)
            else:
                premium=0
            return premium    

        #stoploss function 
        def stoploss(premium,spot,type,diff,trade_type,sl_flag):   
            if sl_flag==True:
                if trade_type=='BUY':
                    if type=='POINTS':
                        premium=premium-diff                
                        spot=spot-diff
                    elif type=='PERCENTAGE':
                        premium=premium*((100-diff)/100)                
                        spot=spot*((100-diff)/100)
                elif trade_type=='SELL':
                    if type=='POINTS':
                        premium=premium+diff                
                        spot=spot+diff
                    elif type=='PERCENTAGE':
                        premium=premium*((100+diff)/100)                
                        spot=spot*((100+diff)/100)
            else:
                premium=0
                spot=0
            return premium,spot
            
        #exit function
        def buy_or_sell(trade,entryprice,exitprice):
            if trade=='SELL':
                pnl=(entryprice-exitprice)*qty
            elif trade=='BUY':
                pnl=(exitprice-entryprice)*qty
            return pnl

        #entry function
        def entry_strike(optiontype,selectiontype,closesttype,strike,diff,moneyness,df,i,expiry,year,indexoption):
            dictt_ce={}
            dictt_pe={}
            sett_list_ce=[]
            sett_list_pe=[]
            if optiontype=='CE':
                if selectiontype=='atm_point':        
                    if moneyness=='ITM':
                        strike_ce=strike-diff                
                    elif moneyness=='OTM':
                        strike_ce=strike+diff                
                    elif moneyness=='ATM':
                        strike_ce=strike
                                
                elif selectiontype=='ATM PERCENTAGE':        
                        if moneyness=='ITM':
                            strike_ce=strike*((100-diff)/100)
                            strike_ce=int(round(strike_ce,-2))                    
                        elif moneyness=='OTM':
                            strike_ce=strike*((100+diff)/100)
                            strike_ce=int(round(strike_ce,-2))                    
                        elif moneyness=='ATM':
                            strike_ce=strike
                                
                elif selectiontype=='closest_premium':
                    try:
                        for k in range(0,600,100):
                            call_itm=df[f'{indexoption}{expiry}{year}{strike-k}CE'][i]
                            dictt_ce.update({strike-k:call_itm})                    
                            sett_list_ce.append(call_itm)
                            
                    except Exception:
                        pass
                    try:
                        for j in range(0,4600,100):
                            call_otm=df[f'{indexoption}{expiry}{year}{strike+j}CE'][i]
                            dictt_ce.update({strike+j:call_otm})              
                            sett_list_ce.append(call_otm)
                            
                    except Exception:
                        pass
                    
                    # text_file.write(dictt_ce)
                    # text_file.write(dictt_pe)
                    if closesttype=='near':
                        
                        premium_ce=min(sett_list_ce,key = lambda x: abs(x-diff))        
                        strike_ce=[strik for strik, prem in dictt_ce.items() if prem == premium_ce]   
                        strike_ce=strike_ce[0]           
                        
                    if closesttype=='greater':
                        
                        # text_file.write(sett_list_ce)
                        # text_file.write(sett_list_pe)
                        premium_ce=min([ i for i in sett_list_ce if i >= diff], key=lambda x:abs(x-diff))        
                        strike_ce=[strik for strik, prem in dictt_ce.items() if prem == premium_ce]   
                        strike_ce=strike_ce[0]          
                        
                    if closesttype=='less':
                        

                        premium_ce=min([ i for i in sett_list_ce if i <= diff], key=lambda x:abs(x-diff))        
                        strike_ce=[strik for strik, prem in dictt_ce.items() if prem == premium_ce]   
                        strike_ce=strike_ce[0]  
                return strike_ce    
                    
            if optiontype=='PE':
                if selectiontype=='atm_point':        
                    if moneyness=='ITM':                
                        strike_pe=strike+diff
                    elif moneyness=='OTM':                
                        strike_pe=strike-diff
                    elif moneyness=='ATM':                
                        strike_pe=strike            
                elif selectiontype=='ATM PERCENTAGE':        
                        if moneyness=='ITM':                    
                            strike_pe=strike*((100+diff)/100)
                            strike_pe=int(round(strike_pe,-2))
                        elif moneyness=='OTM':                    
                            strike_pe=strike*((100-diff)/100)
                            strike_pe=int(round(strike_pe,-2))
                        elif moneyness=='ATM':                    
                            strike_pe=strike        
                elif selectiontype=='closest_premium':
                    try:
                        for k in range(0,600,100):                                   
                            put_itm=df[f'{indexoption}{expiry}{year}{strike+k}PE'][i]
                            dictt_pe.update({strike+k:put_itm})   

                            sett_list_pe.append(put_itm)
                    except Exception:
                        pass
                    try:
                        for j in range(0,4600,100):                                    
                            put_otm=df[f'{indexoption}{expiry}{year}{strike-j}PE'][i]
                            dictt_pe.update({strike-j:put_otm})   
                            sett_list_pe.append(put_otm)  
                    except Exception:
                        pass
                    
                    # text_file.write(dictt_ce)
                    # text_file.write(dictt_pe)
                    if closesttype=='near':        
                        
                        premium_pe=min(sett_list_pe,key = lambda x: abs(x-diff))        
                        strike_pe=[strik for strik, prem in dictt_pe.items() if prem == premium_pe]
                        strike_pe=strike_pe[0]
                    if closesttype=='greater':
                    
                        # text_file.write(sett_list_ce)
                        # text_file.write(sett_list_pe)               
                    
                        premium_pe=min([ i for i in sett_list_pe if i >= diff], key=lambda x:abs(x-diff))        
                        strike_pe=[strik for strik, prem in dictt_pe.items() if prem == premium_pe]
                        strike_pe=strike_pe[0]
                    if closesttype=='less':       
                    
                        premium_pe=min([ i for i in sett_list_pe if i <= diff], key=lambda x:abs(x-diff))        
                        strike_pe=[strik for strik, prem in dictt_pe.items() if prem == premium_pe]
                        strike_pe=strike_pe[0]
                return strike_pe
            


            #PATH
        
        path_bnf_23=r'E:\EzQuant\Data\2023 BNF 6 WEEK BREAKDOWN/' #2022 df
        path_bnf_22 = "files/bnf_2022/"
        # path_bnf_22 = r'D:\EzQuant\Data\BNF 2022/'
        # path_bnf_22 = r'E:\EzQuant\Data\SendAnywhere_444716\2022 BNF/'
        path_bnf_21=r'E:\EzQuant\Data\BNF 2021/' #2021 df bnf
        path_bnf_20=r'E:\EzQuant\Data\BNF 2020/' #2020 df bnf
        path_nf_20=r'E:\EzQuant\Data\NF 2020/' #2020 df nf
        path_nf_21=r'E:\EzQuant\Data\NF 2021/' #2021 df nf
        path_nf_22=r'E:\EzQuant\Data\Nifty 22 Final\2022 NF 6 WEEK BREAKDOWN/' #2022 df nf
        path_nf_23=r'E:\EzQuant\Data\Nifty 23 Final\2023 NF 6 WEEK BREAKDOWN/'
        path_fnf_21=r'D:\ALL COMPLETED DATA\WEEK WISE BREAKDOWN\FNF\2021/'
        path_fnf_22=r'D:\ALL COMPLETED DATA\WEEK WISE BREAKDOWN\FNF\2022/'
        path_fnf_23=r'D:\ALL COMPLETED DATA\WEEK WISE BREAKDOWN\FNF\2023/'

        # df = pd.read_csv('completecsv11.csv')

        # for index, row in df.iterrows():
        #     if row[0]=="trading_instrument":
        #         if row[1]=='1':
        #             n=52
        #             p=76
                
        #         elif row[1]=='2':
        #             n=233
        #             p=257

        #         elif row[1]=='3':
        #             n=320
        #             p=344

        #-105 to -52 BNF 20
        #-52 TO 0 BNF 21
        # 0 TO 52 BNF 22
        # 52 TO 76 BNF 23
        # 76 TO 129 NF 20
        # 129 TO 181 NF 21
        # 181 TO 233 NF 22
        # 233 TO 257 NF 23
        #257 to 268 FNF 21
        #268 TO 320 FNF 22~
        #320 TO 344 FNF 23




        for xx in range(0, 10):

            if flag != True:
                    
                if(xx == -105):	
                    df=(pd.read_parquet(f"{path_bnf_20}OV_02JAN20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY02JAN20" 
                    text_file.write("For 02 JAN Expiry\n")
                    
                if(xx == -104):		
                    df=(pd.read_parquet(f"{path_bnf_20}OV_09JAN20BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY09JAN20" 
                    text_file.write("For 09 JAN Expiry\n")
                    
                if(xx == -103):
                    df=(pd.read_parquet(f"{path_bnf_20}OV_16JAN20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY16JAN20" 
                    text_file.write("For 16 JAN Expiry\n")
                    
                if(xx == -102):
                    df=(pd.read_parquet(f"{path_bnf_20}OV_23JAN20BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY23JAN20" 
                    text_file.write("For 23 JAN Expiry\n")

                if(xx == -101):
                    df=(pd.read_parquet(f"{path_bnf_20}OV_30JAN20BNF_week_0.parquet")) 
                    start_index = 1350000 
                    prefix = "BANKNIFTY30JAN20" 
                    text_file.write("For 30 JAN Expiry\n")

                if(xx == -100):	
                    df=(pd.read_parquet(f"{path_bnf_20}EC_06FEB20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY06FEB20" 
                    text_file.write("For 06 FEB Expiry\n")
                    
                if(xx == -99):		
                    df=(pd.read_parquet(f"{path_bnf_20}EC_13FEB20BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY13FEB20" 
                    text_file.write("For 13 FEB Expiry\n")
                            
                
                if(xx == -98):
                    df=(pd.read_parquet(f"{path_bnf_20}EC_20FEB20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY20FEB20" 
                    text_file.write("For 20 FEB Expiry\n")


                if(xx == -97):
                    df=(pd.read_parquet(f"{path_bnf_20}EC_27FEB20BNF_week_0.parquet")) 
                    start_index = 1260000 
                    prefix = "BANKNIFTY27FEB20" 
                    text_file.write("For 27 FEB Expiry\n")

                if(xx == -96):
                    df=(pd.read_parquet(f"{path_bnf_20}AN_05MAR20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY05MAR20" 
                    text_file.write("For 05 MAR Expiry\n")

                if(xx == -95):
                    df=(pd.read_parquet(f"{path_bnf_20}AN_12MAR20BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY12MAR20" 
                    text_file.write("For 12 MAR Expiry\n")

                if(xx == -94):
                    df=(pd.read_parquet(f"{path_bnf_20}AN_19MAR20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY19MAR20" 
                    text_file.write("For 19 MAR Expiry\n")
                        
                if(xx == -93):
                    df=(pd.read_parquet(f"{path_bnf_20}AN_26MAR20BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY26MAR20" 
                    text_file.write("For 26 MAR Expiry\n")

                if(xx == -92):	
                    df=(pd.read_parquet(f"{path_bnf_20}EB_01APR20BNF_week_0.parquet")) 
                    start_index = 787500 
                    prefix = "BANKNIFTY01APR20" 
                    text_file.write("For 01 APR Expiry\n")

                if(xx == -91):		
                    df=(pd.read_parquet(f"{path_bnf_20}EB_09APR20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY09APR20" 
                    text_file.write("For 09 APR Expiry\n")

                if(xx == -90):
                    df=(pd.read_parquet(f"{path_bnf_20}EB_16APR20BNF_week_0.parquet")) 
                    start_index = 1035000 
                    prefix = "BANKNIFTY16APR20" 
                    text_file.write("For 16 APR Expiry\n")

                if(xx == -89):
                    df=(pd.read_parquet(f"{path_bnf_20}EB_23APR20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY23APR20" 
                    text_file.write("For 23 APR Expiry\n")

                if(xx == -88):
                    df=(pd.read_parquet(f"{path_bnf_20}EB_30APR20BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY30APR20" 
                    text_file.write("For 30 APR Expiry\n")
                    
                if(xx == -87):	
                    df=(pd.read_parquet(f"{path_bnf_20}AR_07MAY20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY07MAY20" 
                    text_file.write("For 07 MAY Expiry\n")
                    
                if(xx == -86):		
                    df=(pd.read_parquet(f"{path_bnf_20}AR_14MAY20BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY14MAY20" 
                    text_file.write("For 14 MAY Expiry\n")
                    
                if(xx == -85):	
                    df=(pd.read_parquet(f"{path_bnf_20}AR_21MAY20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY21MAY20" 
                    text_file.write("For 21 MAY Expiry\n")
                    
                if(xx == -84):	
                    df=(pd.read_parquet(f"{path_bnf_20}AR_28MAY20BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY28MAY20" 
                    text_file.write("For 28 MAY Expiry\n")
                    
                if(xx == -83):	
                    df=(pd.read_parquet(f"{path_bnf_20}PR_04JUN20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY04JUN20" 
                    text_file.write("For 04 JUN Expiry\n")
                

                if(xx == -82):	
                    df=(pd.read_parquet(f"{path_bnf_20}PR_11JUN20BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY11JUN20" 
                    text_file.write("For 11 JUN Expiry\n")
                
                if(xx == -81):	
                    df=(pd.read_parquet(f"{path_bnf_20}PR_18JUN20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY18JUN20" 
                    text_file.write("For 18 JUN Expiry\n")
                
                if(xx == -80):	
                    df=(pd.read_parquet(f"{path_bnf_20}PR_25JUN20BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY25JUN20" 
                    text_file.write("For 25 JUN Expiry\n")

                if(xx == -79):	
                    df=(pd.read_parquet(f"{path_bnf_20}AY_02JUL20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY02JUL20" 
                    text_file.write("For 02 JUL Expiry\n")
                
                if(xx == -78):	
                    df=(pd.read_parquet(f"{path_bnf_20}AY_09JUL20BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY09JUL20" 
                    text_file.write("For 09 JUL Expiry\n")
                
                if(xx == -77):	
                    df=(pd.read_parquet(f"{path_bnf_20}AY_16JUL20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY16JUL20" 
                    text_file.write("For 16 JUL Expiry\n")

                if(xx == -76):	
                    df=(pd.read_parquet(f"{path_bnf_20}AY_23JUL20BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY23JUL20" 
                    text_file.write("For 23 JUL Expiry\n")

                if(xx == -75):	

                    df=(pd.read_parquet(f"{path_bnf_20}AY_30JUL20BNF_week_0.parquet")) 
                    start_index = 1350000 
                    prefix = "BANKNIFTY30JUL20" 
                    text_file.write("For 30 JUL Expiry\n")

                if(xx == -74):	
                    df=(pd.read_parquet(f"{path_bnf_20}UN_06AUG20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY06AUG20" 
                    text_file.write("For 06 AUG Expiry\n")
                
                if(xx == -73):	
                    df=(pd.read_parquet(f"{path_bnf_20}UN_13AUG20BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY13AUG20" 
                    text_file.write("For 13 AUG Expiry\n")
                    
                if(xx == -72):	
                    df=(pd.read_parquet(f"{path_bnf_20}UN_20AUG20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY20AUG20" 
                    text_file.write("For 20 AUG Expiry\n")
                
                if(xx == -71):	
                    df=(pd.read_parquet(f"{path_bnf_20}UN_27AUG20BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY27AUG20" 
                    text_file.write("For 27 AUG Expiry\n")

                if(xx == -70):	
                    df=(pd.read_parquet(f"{path_bnf_20}UL_03SEP20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY03SEP20" 
                    text_file.write("For 03 SEP Expiry\n")
                
                if(xx == -69):	
                    df=(pd.read_parquet(f"{path_bnf_20}UL_10SEP20BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY10SEP20" 
                    text_file.write("For 10 SEP Expiry\n")

                if(xx == -68):	
                    df=(pd.read_parquet(f"{path_bnf_20}UL_17SEP20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY17SEP20" 
                    text_file.write("For 17 SEP Expiry\n")
                        
                if(xx == -67):	
                    df=(pd.read_parquet(f"{path_bnf_20}UL_24SEP20BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY24SEP20" 
                    text_file.write("For 24 SEP Expiry\n")
                
                if(xx == -66):	
                    df=(pd.read_parquet(f"{path_bnf_20}UG_01OCT20BNF_week_0.parquet")) 
                    start_index = 787500 
                    prefix = "BANKNIFTY01OCT20" 
                    text_file.write("For 01 OCT Expiry\n")
                        
                if(xx == -65):	
                    df=(pd.read_parquet(f"{path_bnf_20}UG_08OCT20BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY08OCT20" 
                    text_file.write("For 08 OCT Expiry\n")

                if(xx == -64):	
                    df=(pd.read_parquet(f"{path_bnf_20}UG_15OCT20BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY15OCT20" 
                    text_file.write("For 15 OCT Expiry\n")
                
                if(xx == -63):	
                    df=(pd.read_parquet(f"{path_bnf_20}UG_22OCT20BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY22OCT20" 
                    text_file.write("For 22 OCT Expiry\n")

                if(xx == -62):	
                    df=(pd.read_parquet(f"{path_bnf_20}UG_29OCT20BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY29OCT20" 
                    text_file.write("For 29 OCT Expiry\n")

                if(xx == -61):	
                    df=(pd.read_parquet(f"{path_bnf_20}EP_05NOV20BNF_week_0.parquet")) 
                    start_index = 877500 
                    prefix = "BANKNIFTY05NOV20" 
                    text_file.write("For 05 NOV Expiry\n")
                if(xx == -60):	
                    df=(pd.read_parquet(f"{path_bnf_20}EP_12NOV20BNF_week_0.parquet")) 
                    start_index = 990000 
                    prefix = "BANKNIFTY12NOV20" 
                    text_file.write("For 12 NOV Expiry\n")

                if(xx == -59):	
                    df=(pd.read_parquet(f"{path_bnf_20}EP_19NOV20BNF_week_0.parquet")) 
                    start_index = 1102500 
                    prefix = "BANKNIFTY19NOV20" 
                    text_file.write("For 19 NOV Expiry\n")

                if(xx == -58):	
                    df=(pd.read_parquet(f"{path_bnf_20}EP_26NOV20BNF_week_0.parquet")) 
                    start_index = 1215000 
                    prefix = "BANKNIFTY26NOV20" 
                    text_file.write("For 26 NOV Expiry\n")

                if(xx == -57):	
                    df=(pd.read_parquet(f"{path_bnf_20}CT_03DEC20BNF_week_0.parquet")) 
                    start_index = 877500 
                    prefix = "BANKNIFTY03DEC20" 
                    text_file.write("For 03 DEC Expiry\n")
                if(xx == -56):	
                    df=(pd.read_parquet(f"{path_bnf_20}CT_10DEC20BNF_week_0.parquet")) 
                    start_index = 990000 
                    prefix = "BANKNIFTY10DEC20" 
                    text_file.write("For 10 DEC Expiry\n")

                if(xx == -55):	
                    df=(pd.read_parquet(f"{path_bnf_20}CT_17DEC20BNF_week_0.parquet")) 
                    start_index = 1102500 
                    prefix = "BANKNIFTY17DEC20" 
                    text_file.write("For 17 DEC Expiry\n")
                
                if(xx == -54):	
                    df=(pd.read_parquet(f"{path_bnf_20}CT_24DEC20BNF_week_0.parquet")) 
                    start_index = 1215000 
                    prefix = "BANKNIFTY24DEC20" 
                    text_file.write("For 24 DEC Expiry\n")

                if(xx == -53):	
                    df=(pd.read_parquet(f"{path_bnf_20}CT_31DEC20BNF_week_0.parquet")) 
                    start_index = 1327500 
                    prefix = "BANKNIFTY31DEC20" 
                    text_file.write("For 31 DEC Expiry\n")
                
                
                
                if(xx == -52):	
                    df=(pd.read_parquet(f"{path_bnf_21}OV_07JAN21BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY07JAN21" 
                    text_file.write("For 07 JAN Expiry\n")
                    
                if(xx == -51):		
                    df=(pd.read_parquet(f"{path_bnf_21}OV_14JAN21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY14JAN21" 
                    text_file.write("For 14 JAN Expiry\n")
                    
                if(xx == -50):
                    df=(pd.read_parquet(f"{path_bnf_21}OV_21JAN21BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY21JAN21" 
                    text_file.write("For 21 JAN Expiry\n")
                    
                if(xx == -49):
                    df=(pd.read_parquet(f"{path_bnf_21}OV_28JAN21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY28JAN21" 
                    text_file.write("For 28 JAN Expiry\n")

                if(xx == -48):	
                    df=(pd.read_parquet(f"{path_bnf_21}EC_04FEB21BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY04FEB21" 
                    text_file.write("For 04 FEB Expiry\n")
                    
                if(xx == -47):		
                    df=(pd.read_parquet(f"{path_bnf_21}EC_11FEB21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY11FEB21" 
                    text_file.write("For 11 FEB Expiry\n")
                    
                
                if(xx == -46):
                    df=(pd.read_parquet(f"{path_bnf_21}EC_18FEB21BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY18FEB21" 
                    text_file.write("For 18 FEB Expiry\n")


                if(xx == -45):
                    df=(pd.read_parquet(f"{path_bnf_21}EC_25FEB21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY25FEB21" 
                    text_file.write("For 25 FEB Expiry\n")

                if(xx == -44):
                    df=(pd.read_parquet(f"{path_bnf_21}AN_04MAR21BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY04MAR21" 
                    text_file.write("For 04 MAR Expiry\n")

                if(xx == -43):
                    df=(pd.read_parquet(f"{path_bnf_21}AN_10MAR21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY10MAR21" 
                    text_file.write("For 10 MAR Expiry\n")

                if(xx == -42):
                    df=(pd.read_parquet(f"{path_bnf_21}AN_18MAR21BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY18MAR21" 
                    text_file.write("For 18 MAR Expiry\n")
                        
                if(xx == -41):
                    df=(pd.read_parquet(f"{path_bnf_21}AN_25MAR21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY25MAR21" 
                    text_file.write("For 25 MAR Expiry\n")


                if(xx == -40):	
                    df=(pd.read_parquet(f"{path_bnf_21}EB_01APR21BNF_week_0.parquet")) 
                    start_index = 787500 
                    prefix = "BANKNIFTY01APR21" 
                    text_file.write("For 01 APR Expiry\n")

                if(xx == -39):		
                    df=(pd.read_parquet(f"{path_bnf_21}EB_08APR21BNF_week_0.parquet")) 
                    start_index = 922500 
                    prefix = "BANKNIFTY08APR21" 
                    text_file.write("For 08 APR Expiry\n")

                if(xx == -38):
                    df=(pd.read_parquet(f"{path_bnf_21}EB_15APR21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY15APR21" 
                    text_file.write("For 15 APR Expiry\n")

                if(xx == -37):
                    df=(pd.read_parquet(f"{path_bnf_21}EB_22APR21BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY22APR21" 
                    text_file.write("For 22 APR Expiry\n")

                if(xx == -36):
                    df=(pd.read_parquet(f"{path_bnf_21}EB_29APR21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY29APR21" 
                    text_file.write("For 29 APR Expiry\n")

                if(xx == -35):	
                    df=(pd.read_parquet(f"{path_bnf_21}AR_06MAY21BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY06MAY21" 
                    text_file.write("For 06 MAY Expiry\n")
                    
                if(xx == -34):		
                    df=(pd.read_parquet(f"{path_bnf_21}AR_12MAY21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY12MAY21" 
                    text_file.write("For 12 MAY Expiry\n")
                    
                if(xx == -33):	
                    df=(pd.read_parquet(f"{path_bnf_21}AR_20MAY21BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY20MAY21" 
                    text_file.write("For 20 MAY Expiry\n")
                    
                if(xx == -32):	
                    df=(pd.read_parquet(f"{path_bnf_21}AR_27MAY21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY27MAY21" 
                    text_file.write("For 27 MAY Expiry\n")	


                if(xx == -31):	
                    df=(pd.read_parquet(f"{path_bnf_21}PR_03JUN21BNF_week_0.parquet")) 
                    start_index = 877500 
                    prefix = "BANKNIFTY03JUN21" 
                    text_file.write("For 03 JUN Expiry\n")
                

                if(xx == -30):	
                    df=(pd.read_parquet(f"{path_bnf_21}PR_10JUN21BNF_week_0.parquet")) 
                    start_index = 990000 
                    prefix = "BANKNIFTY10JUN21" 
                    text_file.write("For 10 JUN Expiry\n")
                
                if(xx == -29):	
                    df=(pd.read_parquet(f"{path_bnf_21}PR_17JUN21BNF_week_0.parquet")) 
                    start_index = 1102500 
                    prefix = "BANKNIFTY17JUN21" 
                    text_file.write("For 17 JUN Expiry\n")
                
                if(xx == -28):	
                    df=(pd.read_parquet(f"{path_bnf_21}PR_24JUN21BNF_week_0.parquet")) 
                    start_index = 1215000 
                    prefix = "BANKNIFTY24JUN21" 
                    text_file.write("For 24 JUN Expiry\n")
                        
                



                if(xx == -27):	
                    df=(pd.read_parquet(f"{path_bnf_21}AY_01JUL21BNF_week_0.parquet")) 
                    start_index = 787500 
                    prefix = "BANKNIFTY01JUL21" 
                    text_file.write("For 01 JUL Expiry\n")
                
                if(xx == -26):	
                    df=(pd.read_parquet(f"{path_bnf_21}AY_08JUL21BNF_week_0.parquet")) 
                    start_index = 90000 
                    prefix = "BANKNIFTY08JUL21" 
                    text_file.write("For 08 JUL Expiry\n")
                
                if(xx == -25):	
                    df=(pd.read_parquet(f"{path_bnf_21}AY_15JUL21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY15JUL21" 
                    text_file.write("For 15 JUL Expiry\n")

                if(xx == -24):	
                    df=(pd.read_parquet(f"{path_bnf_21}AY_22JUL21BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY22JUL21" 
                    text_file.write("For 22 JUL Expiry\n")

                if(xx == -23):	

                    df=(pd.read_parquet(f"{path_bnf_21}AY_29JUL21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY29JUL21" 
                    text_file.write("For 29 JUL Expiry\n")


                if(xx == -22):	
                    df=(pd.read_parquet(f"{path_bnf_21}UN_05AUG21BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY05AUG21" 
                    text_file.write("For 05 AUG Expiry\n")
                
                if(xx == -21):	
                    df=(pd.read_parquet(f"{path_bnf_21}UN_12AUG21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY12AUG21" 
                    text_file.write("For 12 AUG Expiry\n")

                if(xx == -20):	
                    df=(pd.read_parquet(f"{path_bnf_21}UN_18AUG21BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY18AUG21" 
                    text_file.write("For 18 AUG Expiry\n")
                
                if(xx == -19):	
                    df=(pd.read_parquet(f"{path_bnf_21}UN_26AUG21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY26AUG21" 
                    text_file.write("For 26 AUG Expiry\n")

                if(xx == -18):	
                    df=(pd.read_parquet(f"{path_bnf_21}UL_02SEP21BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY02SEP21" 
                    text_file.write("For 02 SEP Expiry\n")
                
                if(xx == -17):	
                    df=(pd.read_parquet(f"{path_bnf_21}UL_09SEP21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY09SEP21" 
                    text_file.write("For 09 SEP Expiry\n")

                if(xx == -16):	
                    df=(pd.read_parquet(f"{path_bnf_21}UL_16SEP21BNF_week_0.parquet")) 
                    start_index = 1147500 
                    prefix = "BANKNIFTY16SEP21" 
                    text_file.write("For 16 SEP Expiry\n")
                        
                if(xx == -15):	
                    df=(pd.read_parquet(f"{path_bnf_21}UL_23SEP21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY23SEP21" 
                    text_file.write("For 23 SEP Expiry\n")
                
                if(xx == -14):	
                    df=(pd.read_parquet(f"{path_bnf_21}UL_30SEP21BNF_week_0.parquet")) 
                    start_index = 1350000 
                    prefix = "BANKNIFTY30SEP21" 
                    text_file.write("For 30 SEP Expiry\n")

                if(xx == -13):	
                    df=(pd.read_parquet(f"{path_bnf_21}UG_07OCT21BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY07OCT21" 
                    text_file.write("For 07 OCT Expiry\n")
                
                if(xx == -12):	
                    df=(pd.read_parquet(f"{path_bnf_21}UG_14OCT21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY14OCT21" 
                    text_file.write("For 14 OCT Expiry\n")

                if(xx == -11):	
                    df=(pd.read_parquet(f"{path_bnf_21}UG_21OCT21BNF_week_0.parquet")) 
                    start_index = 1147500 
                    prefix = "BANKNIFTY21OCT21" 
                    text_file.write("For 21 OCT Expiry\n")
                
                if(xx == -10):	
                    df=(pd.read_parquet(f"{path_bnf_21}UG_28OCT21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY28OCT21" 
                    text_file.write("For 28 OCT Expiry\n")


                if(xx == -9):	
                    df=(pd.read_parquet(f"{path_bnf_21}EP_03NOV21BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY03NOV21" 
                    text_file.write("For 03 NOV Expiry\n")
                if(xx == -8):	
                    df=(pd.read_parquet(f"{path_bnf_21}EP_11NOV21BNF_week_0.parquet")) 
                    start_index = 1035000 
                    prefix = "BANKNIFTY11NOV21" 
                    text_file.write("For 11 NOV Expiry\n")

                if(xx == -7):	
                    df=(pd.read_parquet(f"{path_bnf_21}EP_18NOV21BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY18NOV21" 
                    text_file.write("For 18 NOV Expiry\n")

                if(xx == -6):	
                    df=(pd.read_parquet(f"{path_bnf_21}EP_25NOV21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY25NOV21" 
                    text_file.write("For 25 NOV Expiry\n")


                if(xx == -5):	
                    df=(pd.read_parquet(f"{path_bnf_21}CT_02DEC21BNF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "BANKNIFTY02DEC21" 
                    text_file.write("For 02 DEC Expiry\n")

                if(xx == -4):	
                    df=(pd.read_parquet(f"{path_bnf_21}CT_09DEC21BNF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "BANKNIFTY09DEC21" 
                    text_file.write("For 09 DEC Expiry\n")

                if(xx == -3):	
                    df=(pd.read_parquet(f"{path_bnf_21}CT_16DEC21BNF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "BANKNIFTY16DEC21" 
                    text_file.write("For 16 DEC Expiry\n")
                
                if(xx == -2):	
                    df=(pd.read_parquet(f"{path_bnf_21}CT_23DEC21BNF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "BANKNIFTY23DEC21" 
                    text_file.write("For 23 DEC Expiry\n")

                if(xx == -1):	
                    df=(pd.read_parquet(f"{path_bnf_21}CT_30DEC21BNF_week_0.parquet")) 
                    start_index = 1350000 
                    prefix = "BANKNIFTY30DEC21" 
                    text_file.write("For 30 DEC Expiry\n")
                    
                
                
                if(xx == 0):	
                    df=(pd.read_parquet(f"{path_bnf_22}03JAN_06JAN_week_0.parquet"))		
                    start_index = 0
                    prefix = "BANKNIFTY06JAN22"
                    text_file.write("For 6 JAN Expiry\n")
                    
                if(xx == 1):		
                    df=(pd.read_parquet(f"{path_bnf_22}03JAN_13JAN_week_0.parquet"))		
                    start_index = 90000
                    prefix = "BANKNIFTY13JAN22"
                    text_file.write("For 13 JAN Expiry\n")
                    
                if(xx == 2):
                    df=(pd.read_parquet(f"{path_bnf_22}03JAN_20JAN_week_0.parquet"))		
                    start_index = 202500
                    prefix = "BANKNIFTY20JAN22"
                    text_file.write("For 20 JAN Expiry\n")
                    
                if(xx == 3):
                    df=(pd.read_parquet(f"{path_bnf_22}03JAN_27JAN_week_0.parquet"))		
                    start_index = 315000
                    prefix = "BANKNIFTY27JAN22"
                    text_file.write("For 27 JAN Expiry\n")

                if(xx == 4):	
                    df=(pd.read_parquet(f"{path_bnf_22}28JAN_03FEB_week_0.parquet"))		
                    start_index = 0
                    prefix = "BANKNIFTY03FEB22"
                    text_file.write("For 3 FEB Expiry\n")
                    
                if(xx == 5):		
                    df=(pd.read_parquet(f"{path_bnf_22}28JAN_10FEB_week_0.parquet"))		
                    start_index = 112500
                    prefix = "BANKNIFTY10FEB22"
                    text_file.write("For 10 FEB Expiry\n")
                    
                if(xx == 6):
                    df=(pd.read_parquet(f"{path_bnf_22}28JAN_17FEB_week_0.parquet"))		
                    start_index = 225000
                    prefix = "BANKNIFTY17FEB22"
                    text_file.write("For 17 FEB Expiry\n")
                
                if(xx == 7):
                    df=(pd.read_parquet(f"{path_bnf_22}28JAN_24FEB_week_0.parquet"))		
                    start_index = 337500
                    prefix = "BANKNIFTY24FEB22"
                    text_file.write("For 24 FEB Expiry\n")

                if(xx == 8):
                    df=(pd.read_parquet(f"{path_bnf_22}25FEB_03MAR_week_0.parquet"))		
                    start_index = 0
                    prefix = "BANKNIFTY03MAR22"
                    text_file.write("For 03 MAR Expiry\n")

                if(xx == 9):
                    df=(pd.read_parquet(f"{path_bnf_22}25FEB_10MAR_week_0.parquet"))		
                    start_index = 112500
                    prefix = "BANKNIFTY10MAR22"
                    text_file.write("For 10 MAR Expiry\n")

                if(xx == 10):
                    df=(pd.read_parquet(f"{path_bnf_22}25FEB_17MAR_week_0.parquet"))		
                    start_index = 225000
                    prefix = "BANKNIFTY17MAR22"
                    text_file.write("For 17 MAR Expiry\n")

                if(xx == 11):
                    df=(pd.read_parquet(f"{path_bnf_22}25FEB_24MAR_week_0.parquet"))		
                    start_index = 337500
                    prefix = "BANKNIFTY24MAR22"
                    text_file.write("For 24 MAR Expiry\n")
                
                if(xx == 12):
                    df=(pd.read_parquet(f"{path_bnf_22}25FEB_31MAR_week_0.parquet"))		
                    start_index = 450000
                    prefix = "BANKNIFTY31MAR22"
                    text_file.write("For 31 MAR Expiry\n")

                if(xx == 13):	
                    df=(pd.read_parquet(f"{path_bnf_22}01MAR_07APR_week_0.parquet"))		
                    start_index = 0
                    prefix = "BANKNIFTY07APR22"
                    text_file.write("For 7 April Expiry\n")

                if(xx == 14):		
                    df=(pd.read_parquet(f"{path_bnf_22}01MAR_13APR_week_0.parquet"))		
                    start_index = 112500
                    prefix = "BANKNIFTY13APR22"
                    text_file.write("For 13 April Expiry\n")

                if(xx == 15):
                    df=(pd.read_parquet(f"{path_bnf_22}01MAR_21APR_week_0.parquet"))		
                    start_index = 225000
                    prefix = "BANKNIFTY21APR22"
                    text_file.write("For 21 April Expiry\n")

                if(xx == 16):
                    df=(pd.read_parquet(f"{path_bnf_22}01MAR_28APR_week_0.parquet"))		
                    start_index = 337500
                    prefix = "BANKNIFTY28APR22"
                    text_file.write("For 28 April Expiry\n")

                if(xx == 17):	
                    df=(pd.read_parquet(f"{path_bnf_22}29APR_05MAY_week_0.parquet"))		
                    start_index = 0
                    prefix = "BANKNIFTY05MAY22"
                    text_file.write("For 5 MAY Expiry\n")
                    
                if(xx == 18):		
                    df=(pd.read_parquet(f"{path_bnf_22}29APR_12MAY_week_0.parquet"))		
                    start_index = 112500
                    prefix = "BANKNIFTY12MAY22"
                    text_file.write("For 12 MAY Expiry\n")
                    
                if(xx == 19):	
                    df=(pd.read_parquet(f"{path_bnf_22}29APR_19MAY_week_0.parquet"))		
                    start_index = 225000
                    prefix = "BANKNIFTY19MAY22"
                    text_file.write("For 19 MAY Expiry\n")
                    
                if(xx == 20):	
                    df=(pd.read_parquet(f"{path_bnf_22}29APR_26MAY_week_0.parquet"))		
                    start_index = 337500
                    prefix = "BANKNIFTY26MAY22"
                    text_file.write("For 26 MAY Expiry\n")	

                if(xx == 21):	
                    df=(pd.read_parquet(f"{path_bnf_22}27MAY_02JUN_week_0.parquet"))		
                    start_index = 0
                    prefix = "BANKNIFTY02JUN22"
                    text_file.write("For 02 JUN Expiry\n")
                

                if(xx == 22):	
                    df=(pd.read_parquet(f"{path_bnf_22}27MAY_09JUN_week_0.parquet"))		
                    start_index = 112500
                    prefix = "BANKNIFTY09JUN22"
                    text_file.write("For 09 JUN Expiry\n")
                
                if(xx == 23):	
                    df=(pd.read_parquet(f"{path_bnf_22}27MAY_16JUN_week_0.parquet"))		
                    start_index = 225000  
                    prefix = "BANKNIFTY16JUN22"
                    text_file.write("For 16 JUN Expiry\n")
                
                if(xx == 24):	
                    df=(pd.read_parquet(f"{path_bnf_22}27MAY_23JUN_week_0.parquet"))		
                    start_index = 337500 
                    prefix = "BANKNIFTY23JUN22"
                    text_file.write("For 23 JUN Expiry\n")
                
                if(xx == 25):	
                    df=(pd.read_parquet(f"{path_bnf_22}27MAY_30JUN_week_0.parquet"))		
                    start_index = 450000  
                    prefix = "BANKNIFTY30JUN22"
                    text_file.write("For 30 JUN Expiry\n")

                if(xx == 26):	
                    df=(pd.read_parquet(f"{path_bnf_22}01JUL_07JUL_week_0.parquet"))		
                    start_index = 0  
                    prefix = "BANKNIFTY07JUL22"
                    text_file.write("For 07 JUL Expiry\n")
                
                if(xx == 27):	
                    df=(pd.read_parquet(f"{path_bnf_22}01JUL_14JUL_week_0.parquet"))		
                    start_index = 112500  
                    prefix = "BANKNIFTY14JUL22"
                    text_file.write("For 14 JUL Expiry\n")
                
                if(xx == 28):	
                    df=(pd.read_parquet(f"{path_bnf_22}01JUL_21JUL_week_0.parquet"))		
                    start_index = 225000   
                    prefix = "BANKNIFTY21JUL22"
                    text_file.write("For 21 JUL Expiry\n")

                if(xx == 29):	
                    df=(pd.read_parquet(f"{path_bnf_22}01JUL_28JUL_week_0.parquet"))		
                    start_index = 337500    
                    prefix = "BANKNIFTY28JUL22"
                    text_file.write("For 28 JUL Expiry\n")

                if(xx == 30):	
                    df=(pd.read_parquet(f"{path_bnf_22}29JUL_04AUG_week_0.parquet"))		
                    start_index = 0    
                    prefix = "BANKNIFTY04AUG22"
                    text_file.write("For 04 AUG Expiry\n")
                
                if(xx == 31):	
                    df=(pd.read_parquet(f"{path_bnf_22}29JUL_11AUG_week_0.parquet"))		
                    start_index = 112500     
                    prefix = "BANKNIFTY11AUG22"
                    text_file.write("For 11 AUG Expiry\n")

                if(xx == 32):	
                    df=(pd.read_parquet(f"{path_bnf_22}29JUL_18AUG_week_0.parquet"))		
                    start_index = 225000      
                    prefix = "BANKNIFTY18AUG22"
                    text_file.write("For 18 AUG Expiry\n")
                
                if(xx == 33):	
                    df=(pd.read_parquet(f"{path_bnf_22}29JUL_25AUG_week_0.parquet"))		
                    start_index = 337500       
                    prefix = "BANKNIFTY25AUG22"
                    text_file.write("For 25 AUG Expiry\n")

                if(xx == 34):	
                    df=(pd.read_parquet(f"{path_bnf_22}26AUG_01SEP_week_0.parquet"))		
                    start_index = 0    
                    prefix = "BANKNIFTY01SEP22"
                    text_file.write("For 01 SEP Expiry\n")
                
                if(xx == 35):	
                    df=(pd.read_parquet(f"{path_bnf_22}26AUG_08SEP_week_0.parquet"))		
                    start_index = 112500      
                    prefix = "BANKNIFTY08SEP22"
                    text_file.write("For 08 SEP Expiry\n")

                if(xx == 36):	
                    df=(pd.read_parquet(f"{path_bnf_22}26AUG_15SEP_week_0.parquet"))		
                    start_index = 225000       
                    prefix = "BANKNIFTY15SEP22"
                    text_file.write("For 15 SEP Expiry\n")
                
                if(xx == 37):	
                    df=(pd.read_parquet(f"{path_bnf_22}26AUG_22SEP_week_0.parquet"))		
                    start_index = 337500        
                    prefix = "BANKNIFTY22SEP22"
                    text_file.write("For 22 SEP Expiry\n")
                
                if(xx == 38):	
                    df=(pd.read_parquet(f"{path_bnf_22}26AUG_29SEP_week_0.parquet"))	
                    start_index = 450000        
                    prefix = "BANKNIFTY29SEP22"
                    text_file.write("For 29 SEP Expiry\n")

                if(xx == 39):	
                    df=(pd.read_parquet(f"{path_bnf_22}30SEP_06OCT_week_0.parquet"))		
                    start_index = 0    
                    prefix = "BANKNIFTY06OCT22"
                    text_file.write("For 06 OCT Expiry\n")
                
                if(xx == 40):	
                    df=(pd.read_parquet(f"{path_bnf_22}30SEP_13OCT_week_0.parquet"))		
                    start_index = 112500      
                    prefix = "BANKNIFTY13OCT22"
                    text_file.write("For 13 OCT Expiry\n")

                if(xx == 41):	
                    df=(pd.read_parquet(f"{path_bnf_22}30SEP_20OCT_week_0.parquet"))		
                    start_index = 225000       
                    prefix = "BANKNIFTY20OCT22"
                    text_file.write("For 20 OCT Expiry\n")
                
                if(xx == 42):	
                    df=(pd.read_parquet(f"{path_bnf_22}30SEP_27OCT_week_0.parquet"))		
                    start_index = 337500       
                    prefix = "BANKNIFTY27OCT22"
                    text_file.write("For 27 OCT Expiry\n")

                if(xx == 43):	
                    df=(pd.read_parquet(f"{path_bnf_22}28OCT_03NOV_week_0.parquet"))		
                    start_index = 0    
                    prefix = "BANKNIFTY03NOV22"
                    text_file.write("For 03 NOV Expiry\n")
                
                if(xx == 44):	
                    df=(pd.read_parquet(f"{path_bnf_22}28OCT_10NOV_week_0.parquet"))		
                    start_index = 112500      
                    prefix = "BANKNIFTY10NOV22"
                    text_file.write("For 10 NOV Expiry\n")

                if(xx == 45):	
                    df=(pd.read_parquet(f"{path_bnf_22}28OCT_17NOV_week_0.parquet"))		
                    start_index = 225000       
                    prefix = "BANKNIFTY17NOV22"
                    text_file.write("For 17 NOV Expiry\n")

                if(xx == 46):	
                    df=(pd.read_parquet(f"{path_bnf_22}28OCT_24NOV_week_0.parquet"))		
                    start_index = 337500       
                    prefix = "BANKNIFTY24NOV22"
                    text_file.write("For 24 NOV Expiry\n")

                if(xx == 47):	
                    df=(pd.read_parquet(f"{path_bnf_22}25NOV_01DEC_week_0.parquet"))		
                    start_index = 0    
                    prefix = "BANKNIFTY01DEC22"
                    text_file.write("For 01 DEC Expiry\n")

                if(xx == 48):	
                    df=(pd.read_parquet(f"{path_bnf_22}25NOV_08DEC_week_0.parquet"))		
                    start_index = 112500      
                    prefix = "BANKNIFTY08DEC22"
                    text_file.write("For 08 DEC Expiry\n")

                if(xx == 49):	
                    df=(pd.read_parquet(f"{path_bnf_22}25NOV_15DEC_week_0.parquet"))		
                    start_index = 225000       
                    prefix = "BANKNIFTY15DEC22"
                    text_file.write("For 15 DEC Expiry\n")
                
                if(xx == 50):	
                    df=(pd.read_parquet(f"{path_bnf_22}25NOV_22DEC_week_0.parquet"))		
                    start_index = 337500       
                    prefix = "BANKNIFTY22DEC22"
                    text_file.write("For 22 DEC Expiry\n")

                if(xx == 51):	
                    df=(pd.read_parquet(f"{path_bnf_22}25NOV_29DEC_week_0.parquet"))		
                    start_index = 450000        
                    prefix = "BANKNIFTY29DEC22"
                    text_file.write("For 29 DEC Expiry\n") 
                if(xx == 52):	
                    df=(pd.read_parquet(f"{path_bnf_23}14OCT_05JAN23_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "BANKNIFTY05JAN23"
                    text_file.write("For 5 JAN Expiry 23\n")
                    
                if(xx == 53):		
                    df=(pd.read_parquet(f"{path_bnf_23}14OCT_12JAN23_week_0.parquet"))		
                    start_index = 1350000
                    prefix = "BANKNIFTY12JAN23"
                    text_file.write("For 12 JAN Expiry 23\n")
                    
                if(xx == 54):
                    df=(pd.read_parquet(f"{path_bnf_23}14OCT_19JAN23_week_0.parquet"))		
                    start_index = 1462500
                    prefix = "BANKNIFTY19JAN23"
                    text_file.write("For 19 JAN Expiry 23\n")
                    
                if(xx == 55):
                    df=(pd.read_parquet(f"{path_bnf_23}14OCT_25JAN23_week_0.parquet"))		
                    start_index = 1575000
                    prefix = "BANKNIFTY25JAN23"
                    text_file.write("For 25 JAN Expiry 23\n")
                
                if(xx == 56):	
                    df=(pd.read_parquet(f"{path_bnf_23}04NOV_02FEB23_week_0.parquet"))		
                    start_index = 1350000
                    prefix = "BANKNIFTY02FEB23"
                    text_file.write("For 2 FEB Expiry 23\n")
                    
                if(xx == 57):		
                    df=(pd.read_parquet(f"{path_bnf_23}04NOV_09FEB23_week_0.parquet"))		
                    start_index = 1462500
                    prefix = "BANKNIFTY09FEB23"
                    text_file.write("For 09 FEB Expiry 23\n")
                    
                if(xx == 58):
                    df=(pd.read_parquet(f"{path_bnf_23}04NOV_16FEB23_week_0.parquet"))		
                    start_index = 1575000
                    prefix = "BANKNIFTY16FEB23"
                    text_file.write("For 16 FEB Expiry 23\n")
                
                if(xx == 59):
                    df=(pd.read_parquet(f"{path_bnf_23}04NOV_23FEB23_week_0.parquet"))		
                    start_index = 1687500
                    prefix = "BANKNIFTY23FEB23"
                    text_file.write("For 23 FEB Expiry 23\n")

                if(xx == 60):
                    df=(pd.read_parquet(f"{path_bnf_23}09DEC_02MAR23_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "BANKNIFTY02MAR23"
                    text_file.write("For 02 MAR Expiry 23\n")

                if(xx == 61):
                    df=(pd.read_parquet(f"{path_bnf_23}09DEC_09MAR23_week_0.parquet"))		
                    start_index = 1350000
                    prefix = "BANKNIFTY09MAR23"
                    text_file.write("For 09 MAR Expiry 23\n")

                if(xx == 62):
                    df=(pd.read_parquet(f"{path_bnf_23}09DEC_16MAR23_week_0.parquet"))		
                    start_index = 1462500
                    prefix = "BANKNIFTY16MAR23"
                    text_file.write("For 16 MAR Expiry 23\n")

                if(xx == 63):
                    df=(pd.read_parquet(f"{path_bnf_23}09DEC_23MAR23_week_0.parquet"))		
                    start_index = 1575000  
                    prefix = "BANKNIFTY23MAR23"
                    text_file.write("For 23 MAR Expiry 23\n")
                
                if(xx == 64):
                    df=(pd.read_parquet(f"{path_bnf_23}09DEC_29MAR23_week_0.parquet"))		
                    start_index = 1687500  
                    prefix = "BANKNIFTY29MAR23"
                    text_file.write("For 29 MAR Expiry\n")


                if(xx == 65):	
                    df=(pd.read_parquet(f"{path_bnf_23}13JAN_06APR23_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "BANKNIFTY06APR23"
                    text_file.write("For 6 April Expiry 23\n")

                if(xx == 66):		
                    df=(pd.read_parquet(f"{path_bnf_23}13JAN_13APR23_week_0.parquet"))		
                    start_index = 1372500
                    prefix = "BANKNIFTY13APR23"
                    text_file.write("For 13 April Expiry 23\n")

                if(xx == 67):
                    df=(pd.read_parquet(f"{path_bnf_23}13JAN_20APR23_week_0.parquet"))		
                    start_index = 1485000
                    prefix = "BANKNIFTY20APR23"
                    text_file.write("For 20 April Expiry 23\n")

                if(xx == 68):
                    df=(pd.read_parquet(f"{path_bnf_23}13JAN_27APR23_week_0.parquet"))		
                    start_index = 1575000
                    prefix = "BANKNIFTY27APR23"
                    text_file.write("For 27 April Expiry 27\n")

                if(xx == 69):	
                    df=(pd.read_parquet(f"{path_bnf_23}10FEB_04MAY23_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "BANKNIFTY04MAY23"
                    text_file.write("For 4 MAY Expiry\n")
                    
                if(xx == 70):		
                    df=(pd.read_parquet(f"{path_bnf_23}10FEB_11MAY23_week_0.parquet"))		
                    start_index = 1350000
                    prefix = "BANKNIFTY11MAY23"
                    text_file.write("For 11 MAY Expiry 23\n")
                    
                if(xx == 71):	
                    df=(pd.read_parquet(f"{path_bnf_23}10FEB_18MAY23_week_0.parquet"))		
                    start_index = 1462500
                    prefix = "BANKNIFTY18MAY23"
                    text_file.write("For 18 MAY Expiry 23\n")
                    
                if(xx == 72):	
                    df=(pd.read_parquet(f"{path_bnf_23}10FEB_25MAY23_week_0.parquet"))		
                    start_index = 1575000
                    prefix = "BANKNIFTY25MAY23"
                    text_file.write("For 25 MAY Expiry\n")	

                if(xx == 73):	
                    df=(pd.read_parquet(f"{path_bnf_23}10MAR_01JUN23_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "BANKNIFTY01JUN23"
                    text_file.write("For 01 JUN Expiry 23\n")
                    
                if(xx == 74):	
                    df=(pd.read_parquet(f"{path_bnf_23}10MAR_08JUN23_week_0.parquet"))		
                    start_index = 1350000
                    prefix = "BANKNIFTY08JUN23"
                    text_file.write("For 08 JUN Expiry 23\n")
                
                if(xx == 75):	
                    df=(pd.read_parquet(f"{path_bnf_23}10MAR_15JUN23_week_0.parquet"))		
                    start_index = 1462500
                    prefix = "BANKNIFTY15JUN23"
                    text_file.write("For 15 JUN Expiry 23\n")
                
                if(xx == 76):	
                    df=(pd.read_parquet(f"{path_nf_20}NOV_02JAN20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY02JAN20" 
                    text_file.write("For 02 JAN Expiry\n")
                    
                if(xx == 77):		
                    df=(pd.read_parquet(f"{path_nf_20}NOV_09JAN20NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY09JAN20" 
                    text_file.write("For 09 JAN Expiry\n")
                    
                if(xx == 78):
                    df=(pd.read_parquet(f"{path_nf_20}NOV_16JAN20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY16JAN20" 
                    text_file.write("For 16 JAN Expiry\n")
                    
                if(xx == 79):
                    df=(pd.read_parquet(f"{path_nf_20}NOV_23JAN20NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY23JAN20" 
                    text_file.write("For 23 JAN Expiry\n")

                if(xx == 80):
                    df=(pd.read_parquet(f"{path_nf_20}NOV_30JAN20NF_week_0.parquet")) 
                    start_index = 1350000 
                    prefix = "NIFTY30JAN20" 
                    text_file.write("For 30 JAN Expiry\n")

                if(xx == 81):	
                    df=(pd.read_parquet(f"{path_nf_20}DEC_06FEB20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY06FEB20" 
                    text_file.write("For 06 FEB Expiry\n")
                    
                if(xx == 82):		
                    df=(pd.read_parquet(f"{path_nf_20}DEC_13FEB20NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY13FEB20" 
                    text_file.write("For 13 FEB Expiry\n")
                            
                
                if(xx == 83):
                    df=(pd.read_parquet(f"{path_nf_20}DEC_20FEB20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY20FEB20" 
                    text_file.write("For 20 FEB Expiry\n")


                if(xx == 84):
                    df=(pd.read_parquet(f"{path_nf_20}DEC_27FEB20NF_week_0.parquet")) 
                    start_index = 1260000 
                    prefix = "NIFTY27FEB20" 
                    text_file.write("For 27 FEB Expiry\n")

                if(xx == 85):
                    df=(pd.read_parquet(f"{path_nf_20}JAN_05MAR20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY05MAR20" 
                    text_file.write("For 05 MAR Expiry\n")

                if(xx == 86):
                    df=(pd.read_parquet(f"{path_nf_20}JAN_12MAR20NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY12MAR20" 
                    text_file.write("For 12 MAR Expiry\n")

                if(xx == 87):
                    df=(pd.read_parquet(f"{path_nf_20}JAN_19MAR20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY19MAR20" 
                    text_file.write("For 19 MAR Expiry\n")
                        
                if(xx == 88):
                    df=(pd.read_parquet(f"{path_nf_20}JAN_26MAR20NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY26MAR20" 
                    text_file.write("For 26 MAR Expiry\n")

                if(xx == 89):	
                    df=(pd.read_parquet(f"{path_nf_20}FEB_01APR20NF_week_0.parquet")) 
                    start_index = 787500 
                    prefix = "NIFTY01APR20" 
                    text_file.write("For 01 APR Expiry\n")

                if(xx == 90):		
                    df=(pd.read_parquet(f"{path_nf_20}FEB_09APR20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY09APR20" 
                    text_file.write("For 09 APR Expiry\n")

                if(xx == 91):
                    df=(pd.read_parquet(f"{path_nf_20}FEB_16APR20NF_week_0.parquet")) 
                    start_index = 1035000 
                    prefix = "NIFTY16APR20" 
                    text_file.write("For 16 APR Expiry\n")

                if(xx == 92):
                    df=(pd.read_parquet(f"{path_nf_20}FEB_23APR20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY23APR20" 
                    text_file.write("For 23 APR Expiry\n")

                if(xx == 93):
                    df=(pd.read_parquet(f"{path_nf_20}FEB_30APR20NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY30APR20" 
                    text_file.write("For 30 APR Expiry\n")
                    
                if(xx == 94):	
                    df=(pd.read_parquet(f"{path_nf_20}MAR_07MAY20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY07MAY20" 
                    text_file.write("For 07 MAY Expiry\n")
                    
                if(xx == 95):		
                    df=(pd.read_parquet(f"{path_nf_20}MAR_14MAY20NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY14MAY20" 
                    text_file.write("For 14 MAY Expiry\n")
                    
                if(xx == 96):	
                    df=(pd.read_parquet(f"{path_nf_20}MAR_21MAY20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY21MAY20" 
                    text_file.write("For 21 MAY Expiry\n")
                    
                if(xx == 97):	
                    df=(pd.read_parquet(f"{path_nf_20}MAR_28MAY20NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY28MAY20" 
                    text_file.write("For 28 MAY Expiry\n")
                    
                if(xx == 98):	
                    df=(pd.read_parquet(f"{path_nf_20}APR_04JUN20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY04JUN20" 
                    text_file.write("For 04 JUN Expiry\n")
                

                if(xx == 99):	
                    df=(pd.read_parquet(f"{path_nf_20}APR_11JUN20NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY11JUN20" 
                    text_file.write("For 11 JUN Expiry\n")
                
                if(xx == 100):	
                    df=(pd.read_parquet(f"{path_nf_20}APR_18JUN20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY18JUN20" 
                    text_file.write("For 18 JUN Expiry\n")
                
                if(xx == 101):	
                    df=(pd.read_parquet(f"{path_nf_20}APR_25JUN20NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY25JUN20" 
                    text_file.write("For 25 JUN Expiry\n")

                if(xx == 102):	
                    df=(pd.read_parquet(f"{path_nf_20}MAY_02JUL20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY02JUL20" 
                    text_file.write("For 02 JUL Expiry\n")
                
                if(xx == 103):	
                    df=(pd.read_parquet(f"{path_nf_20}MAY_09JUL20NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY09JUL20" 
                    text_file.write("For 09 JUL Expiry\n")
                
                if(xx == 104):	
                    df=(pd.read_parquet(f"{path_nf_20}MAY_16JUL20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY16JUL20" 
                    text_file.write("For 16 JUL Expiry\n")

                if(xx == 105):	
                    df=(pd.read_parquet(f"{path_nf_20}MAY_23JUL20NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY23JUL20" 
                    text_file.write("For 23 JUL Expiry\n")

                if(xx == 106):	

                    df=(pd.read_parquet(f"{path_nf_20}MAY_30JUL20NF_week_0.parquet")) 
                    start_index = 1350000 
                    prefix = "NIFTY30JUL20" 
                    text_file.write("For 30 JUL Expiry\n")

                if(xx == 107):	
                    df=(pd.read_parquet(f"{path_nf_20}JUN_06AUG20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY06AUG20" 
                    text_file.write("For 06 AUG Expiry\n")
                
                if(xx == 108):	
                    df=(pd.read_parquet(f"{path_nf_20}JUN_13AUG20NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY13AUG20" 
                    text_file.write("For 13 AUG Expiry\n")
                    
                if(xx == 109):	
                    df=(pd.read_parquet(f"{path_nf_20}JUN_20AUG20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY20AUG20" 
                    text_file.write("For 20 AUG Expiry\n")
                
                if(xx == 110):	
                    df=(pd.read_parquet(f"{path_nf_20}JUN_27AUG20NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY27AUG20" 
                    text_file.write("For 27 AUG Expiry\n")

                if(xx == 111):	
                    df=(pd.read_parquet(f"{path_nf_20}JUL_03SEP20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY03SEP20" 
                    text_file.write("For 03 SEP Expiry\n")
                
                if(xx == 112):	
                    df=(pd.read_parquet(f"{path_nf_20}JUL_10SEP20NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY10SEP20" 
                    text_file.write("For 10 SEP Expiry\n")

                if(xx == 113):	
                    df=(pd.read_parquet(f"{path_nf_20}JUL_17SEP20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY17SEP20" 
                    text_file.write("For 17 SEP Expiry\n")
                        
                if(xx == 114):	
                    df=(pd.read_parquet(f"{path_nf_20}JUL_24SEP20NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY24SEP20" 
                    text_file.write("For 24 SEP Expiry\n")
                
                if(xx == 115):	
                    df=(pd.read_parquet(f"{path_nf_20}AUG_01OCT20NF_week_0.parquet")) 
                    start_index = 787500 
                    prefix = "NIFTY01OCT20" 
                    text_file.write("For 01 OCT Expiry\n")
                        
                if(xx == 116):	
                    df=(pd.read_parquet(f"{path_nf_20}AUG_08OCT20NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY08OCT20" 
                    text_file.write("For 08 OCT Expiry\n")

                if(xx == 117):	
                    df=(pd.read_parquet(f"{path_nf_20}AUG_15OCT20NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY15OCT20" 
                    text_file.write("For 15 OCT Expiry\n")
                
                if(xx == 118):	
                    df=(pd.read_parquet(f"{path_nf_20}AUG_22OCT20NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY22OCT20" 
                    text_file.write("For 22 OCT Expiry\n")

                if(xx == 119):	
                    df=(pd.read_parquet(f"{path_nf_20}AUG_29OCT20NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY29OCT20" 
                    text_file.write("For 29 OCT Expiry\n")

                if(xx == 120):	
                    df=(pd.read_parquet(f"{path_nf_20}SEP_05NOV20NF_week_0.parquet")) 
                    start_index = 877500 
                    prefix = "NIFTY05NOV20" 
                    text_file.write("For 05 NOV Expiry\n")
                if(xx == 121):	
                    df=(pd.read_parquet(f"{path_nf_20}SEP_12NOV20NF_week_0.parquet")) 
                    start_index = 990000 
                    prefix = "NIFTY12NOV20" 
                    text_file.write("For 12 NOV Expiry\n")

                if(xx == 122):	
                    df=(pd.read_parquet(f"{path_nf_20}SEP_19NOV20NF_week_0.parquet")) 
                    start_index = 1102500 
                    prefix = "NIFTY19NOV20" 
                    text_file.write("For 19 NOV Expiry\n")

                if(xx == 123):	
                    df=(pd.read_parquet(f"{path_nf_20}SEP_26NOV20NF_week_0.parquet")) 
                    start_index = 1215000 
                    prefix = "NIFTY26NOV20" 
                    text_file.write("For 26 NOV Expiry\n")

                if(xx == 124):	
                    df=(pd.read_parquet(f"{path_nf_20}OCT_03DEC20NF_week_0.parquet")) 
                    start_index = 877500 
                    prefix = "NIFTY03DEC20" 
                    text_file.write("For 03 DEC Expiry\n")
                if(xx == 125):	
                    df=(pd.read_parquet(f"{path_nf_20}OCT_10DEC20NF_week_0.parquet")) 
                    start_index = 990000 
                    prefix = "NIFTY10DEC20" 
                    text_file.write("For 10 DEC Expiry\n")

                if(xx == 126):	
                    df=(pd.read_parquet(f"{path_nf_20}OCT_17DEC20NF_week_0.parquet")) 
                    start_index = 1102500 
                    prefix = "NIFTY17DEC20" 
                    text_file.write("For 17 DEC Expiry\n")
                
                if(xx == 127):	
                    df=(pd.read_parquet(f"{path_nf_20}OCT_24DEC20NF_week_0.parquet")) 
                    start_index = 1215000 
                    prefix = "NIFTY24DEC20" 
                    text_file.write("For 24 DEC Expiry\n")

                if(xx == 128):	
                    df=(pd.read_parquet(f"{path_nf_20}OCT_31DEC20NF_week_0.parquet")) 
                    start_index = 1327500 
                    prefix = "NIFTY31DEC20" 
                    text_file.write("For 31 DEC Expiry\n")    

                if(xx == 129):	
                    df=(pd.read_parquet(f"{path_nf_21}NOV_07JAN21NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY07JAN21" 
                    text_file.write("For 07 JAN Expiry\n")
                    
                if(xx == 130):		
                    df=(pd.read_parquet(f"{path_nf_21}NOV_14JAN21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY14JAN21" 
                    text_file.write("For 14 JAN Expiry\n")
                    
                if(xx == 131):
                    df=(pd.read_parquet(f"{path_nf_21}NOV_21JAN21NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY21JAN21" 
                    text_file.write("For 21 JAN Expiry\n")
                    
                if(xx == 132):
                    df=(pd.read_parquet(f"{path_nf_21}NOV_28JAN21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY28JAN21" 
                    text_file.write("For 28 JAN Expiry\n")

                if(xx == 133):	
                    df=(pd.read_parquet(f"{path_nf_21}DEC_04FEB21NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY04FEB21" 
                    text_file.write("For 04 FEB Expiry\n")
                    
                if(xx == 134):		
                    df=(pd.read_parquet(f"{path_nf_21}DEC_11FEB21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY11FEB21" 
                    text_file.write("For 11 FEB Expiry\n")
                    
                
                if(xx == 135):
                    df=(pd.read_parquet(f"{path_nf_21}DEC_18FEB21NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY18FEB21" 
                    text_file.write("For 18 FEB Expiry\n")


                if(xx == 136):
                    df=(pd.read_parquet(f"{path_nf_21}DEC_25FEB21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY25FEB21" 
                    text_file.write("For 25 FEB Expiry\n")

                if(xx == 137):
                    df=(pd.read_parquet(f"{path_nf_21}JAN_04MAR21NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY04MAR21" 
                    text_file.write("For 04 MAR Expiry\n")

                if(xx == 138):
                    df=(pd.read_parquet(f"{path_nf_21}JAN_10MAR21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY10MAR21" 
                    text_file.write("For 10 MAR Expiry\n")

                if(xx == 139):
                    df=(pd.read_parquet(f"{path_nf_21}JAN_18MAR21NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY18MAR21" 
                    text_file.write("For 18 MAR Expiry\n")
                        
                if(xx == 140):
                    df=(pd.read_parquet(f"{path_nf_21}JAN_25MAR21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY25MAR21" 
                    text_file.write("For 25 MAR Expiry\n")


                if(xx == 141):	
                    df=(pd.read_parquet(f"{path_nf_21}FEB_01APR21NF_week_0.parquet")) 
                    start_index = 787500 
                    prefix = "NIFTY01APR21" 
                    text_file.write("For 01 APR Expiry\n")

                if(xx == 142):		
                    df=(pd.read_parquet(f"{path_nf_21}FEB_08APR21NF_week_0.parquet")) 
                    start_index = 922500 
                    prefix = "NIFTY08APR21" 
                    text_file.write("For 08 APR Expiry\n")

                if(xx == 143):
                    df=(pd.read_parquet(f"{path_nf_21}FEB_15APR21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY15APR21" 
                    text_file.write("For 15 APR Expiry\n")

                if(xx == 144):
                    df=(pd.read_parquet(f"{path_nf_21}FEB_22APR21NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY22APR21" 
                    text_file.write("For 22 APR Expiry\n")

                if(xx == 145):
                    df=(pd.read_parquet(f"{path_nf_21}FEB_29APR21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY29APR21" 
                    text_file.write("For 29 APR Expiry\n")

                if(xx == 146):	
                    df=(pd.read_parquet(f"{path_nf_21}MAR_06MAY21NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY06MAY21" 
                    text_file.write("For 06 MAY Expiry\n")
                    
                if(xx == 147):		
                    df=(pd.read_parquet(f"{path_nf_21}MAR_12MAY21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY12MAY21" 
                    text_file.write("For 12 MAY Expiry\n")
                    
                if(xx == 148):	
                    df=(pd.read_parquet(f"{path_nf_21}MAR_20MAY21NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY20MAY21" 
                    text_file.write("For 20 MAY Expiry\n")
                    
                if(xx == 149):	
                    df=(pd.read_parquet(f"{path_nf_21}MAR_27MAY21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY27MAY21" 
                    text_file.write("For 27 MAY Expiry\n")	


                if(xx == 150):	
                    df=(pd.read_parquet(f"{path_nf_21}APR_03JUN21NF_week_0.parquet")) 
                    start_index = 877500 
                    prefix = "NIFTY03JUN21" 
                    text_file.write("For 03 JUN Expiry\n")
                

                if(xx == 151):	
                    df=(pd.read_parquet(f"{path_nf_21}APR_10JUN21NF_week_0.parquet")) 
                    start_index = 990000 
                    prefix = "NIFTY10JUN21" 
                    text_file.write("For 10 JUN Expiry\n")
                
                if(xx == 152):	
                    df=(pd.read_parquet(f"{path_nf_21}APR_17JUN21NF_week_0.parquet")) 
                    start_index = 1102500 
                    prefix = "NIFTY17JUN21" 
                    text_file.write("For 17 JUN Expiry\n")
                
                if(xx == 153):	
                    df=(pd.read_parquet(f"{path_nf_21}APR_24JUN21NF_week_0.parquet")) 
                    start_index = 1215000 
                    prefix = "NIFTY24JUN21" 
                    text_file.write("For 24 JUN Expiry\n")

                if(xx == 154):	
                    df=(pd.read_parquet(f"{path_nf_21}MAY_01JUL21NF_week_0.parquet")) 
                    start_index = 787500 
                    prefix = "NIFTY01JUL21" 
                    text_file.write("For 01 JUL Expiry\n")
                
                if(xx == 155):	
                    df=(pd.read_parquet(f"{path_nf_21}MAY_08JUL21NF_week_0.parquet")) 
                    start_index = 90000 
                    prefix = "NIFTY08JUL21" 
                    text_file.write("For 08 JUL Expiry\n")
                
                if(xx == 156):	
                    df=(pd.read_parquet(f"{path_nf_21}MAY_15JUL21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY15JUL21" 
                    text_file.write("For 15 JUL Expiry\n")

                if(xx == 157):	
                    df=(pd.read_parquet(f"{path_nf_21}MAY_22JUL21NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY22JUL21" 
                    text_file.write("For 22 JUL Expiry\n")

                if(xx == 158):	

                    df=(pd.read_parquet(f"{path_nf_21}MAY_29JUL21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY29JUL21" 
                    text_file.write("For 29 JUL Expiry\n")


                if(xx == 159):	
                    df=(pd.read_parquet(f"{path_nf_21}JUN_05AUG21NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY05AUG21" 
                    text_file.write("For 05 AUG Expiry\n")
                
                if(xx == 160):	
                    df=(pd.read_parquet(f"{path_nf_21}JUN_12AUG21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY12AUG21" 
                    text_file.write("For 12 AUG Expiry\n")

                if(xx == 161):	
                    df=(pd.read_parquet(f"{path_nf_21}JUN_18AUG21NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY18AUG21" 
                    text_file.write("For 18 AUG Expiry\n")
                
                if(xx == 162):	
                    df=(pd.read_parquet(f"{path_nf_21}JUN_26AUG21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY26AUG21" 
                    text_file.write("For 26 AUG Expiry\n")

                if(xx == 163):	
                    df=(pd.read_parquet(f"{path_nf_21}JUL_02SEP21NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY02SEP21" 
                    text_file.write("For 02 SEP Expiry\n")
                
                if(xx == 164):	
                    df=(pd.read_parquet(f"{path_nf_21}JUL_09SEP21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY09SEP21" 
                    text_file.write("For 09 SEP Expiry\n")

                if(xx == 165):	
                    df=(pd.read_parquet(f"{path_nf_21}JUL_16SEP21NF_week_0.parquet")) 
                    start_index = 1147500 
                    prefix = "NIFTY16SEP21" 
                    text_file.write("For 16 SEP Expiry\n")
                        
                if(xx == 166):	
                    df=(pd.read_parquet(f"{path_nf_21}JUL_23SEP21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY23SEP21" 
                    text_file.write("For 23 SEP Expiry\n")
                
                if(xx == 167):	
                    df=(pd.read_parquet(f"{path_nf_21}JUL_30SEP21NF_week_0.parquet")) 
                    start_index = 1350000 
                    prefix = "NIFTY30SEP21" 
                    text_file.write("For 30 SEP Expiry\n")

                if(xx == 168):	
                    df=(pd.read_parquet(f"{path_nf_21}AUG_07OCT21NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY07OCT21" 
                    text_file.write("For 07 OCT Expiry\n")
                
                if(xx == 169):	
                    df=(pd.read_parquet(f"{path_nf_21}AUG_14OCT21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY14OCT21" 
                    text_file.write("For 14 OCT Expiry\n")

                if(xx == 170):	
                    df=(pd.read_parquet(f"{path_nf_21}AUG_21OCT21NF_week_0.parquet")) 
                    start_index = 1147500 
                    prefix = "NIFTY21OCT21" 
                    text_file.write("For 21 OCT Expiry\n")
                
                if(xx == 171):	
                    df=(pd.read_parquet(f"{path_nf_21}AUG_28OCT21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY28OCT21" 
                    text_file.write("For 28 OCT Expiry\n")


                if(xx == 172):	
                    df=(pd.read_parquet(f"{path_nf_21}SEP_03NOV21NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY03NOV21" 
                    text_file.write("For 03 NOV Expiry\n")
                if(xx == 173):	
                    df=(pd.read_parquet(f"{path_nf_21}SEP_11NOV21NF_week_0.parquet")) 
                    start_index = 1035000 
                    prefix = "NIFTY11NOV21" 
                    text_file.write("For 11 NOV Expiry\n")

                if(xx == 174):	
                    df=(pd.read_parquet(f"{path_nf_21}SEP_18NOV21NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY18NOV21" 
                    text_file.write("For 18 NOV Expiry\n")

                if(xx == 175):	
                    df=(pd.read_parquet(f"{path_nf_21}SEP_25NOV21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY25NOV21" 
                    text_file.write("For 25 NOV Expiry\n")


                if(xx == 176):	
                    df=(pd.read_parquet(f"{path_nf_21}OCT_02DEC21NF_week_0.parquet")) 
                    start_index = 900000 
                    prefix = "NIFTY02DEC21" 
                    text_file.write("For 02 DEC Expiry\n")

                if(xx == 177):	
                    df=(pd.read_parquet(f"{path_nf_21}OCT_09DEC21NF_week_0.parquet")) 
                    start_index = 1012500 
                    prefix = "NIFTY09DEC21" 
                    text_file.write("For 09 DEC Expiry\n")

                if(xx == 178):	
                    df=(pd.read_parquet(f"{path_nf_21}OCT_16DEC21NF_week_0.parquet")) 
                    start_index = 1125000 
                    prefix = "NIFTY16DEC21" 
                    text_file.write("For 16 DEC Expiry\n")
                
                if(xx == 179):	
                    df=(pd.read_parquet(f"{path_nf_21}OCT_23DEC21NF_week_0.parquet")) 
                    start_index = 1237500 
                    prefix = "NIFTY23DEC21" 
                    text_file.write("For 23 DEC Expiry\n")

                if(xx == 180):	
                    df=(pd.read_parquet(f"{path_nf_21}OCT_30DEC21NF_week_0.parquet")) 
                    start_index = 1350000 
                    prefix = "NIFTY30DEC21" 
                    text_file.write("For 30 DEC Expiry\n")
                
                
                if(xx == 181):	
                    df=(pd.read_parquet(f"{path_nf_22}NOV_06JAN22NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY06JAN22"
                    text_file.write("For 6 JAN Expiry\n")
                    
                if(xx == 182):		
                    df=(pd.read_parquet(f"{path_nf_22}NOV_13JAN22NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY13JAN22"
                    text_file.write("For 13 JAN Expiry\n")
                    
                if(xx == 183):
                    df=(pd.read_parquet(f"{path_nf_22}NOV_20JAN22NF_week_0.parquet"))		
                    start_index = 1125000
                    prefix = "NIFTY20JAN22"
                    text_file.write("For 20 JAN Expiry\n")
                    
                if(xx == 184):
                    df=(pd.read_parquet(f"{path_nf_22}NOV_27JAN22NF_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "NIFTY27JAN22"
                    text_file.write("For 27 JAN Expiry\n")

                if(xx == 185):	
                    df=(pd.read_parquet(f"{path_nf_22}DEC_03FEB22NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY03FEB22"
                    text_file.write("For 3 FEB Expiry\n")
                    
                if(xx == 186):		
                    df=(pd.read_parquet(f"{path_nf_22}DEC_10FEB22NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY10FEB22"
                    text_file.write("For 10 FEB Expiry\n")
                    
                if(xx == 187):
                    df=(pd.read_parquet(f"{path_nf_22}DEC_17FEB22NF_week_0.parquet"))		
                    start_index = 1125000
                    prefix = "NIFTY17FEB22"
                    text_file.write("For 17 FEB Expiry\n")
                
                if(xx == 188):
                    df=(pd.read_parquet(f"{path_nf_22}DEC_24FEB22NF_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "NIFTY24FEB22"
                    text_file.write("For 24 FEB Expiry\n")

                if(xx == 189):
                    df=(pd.read_parquet(f"{path_nf_22}JAN_03MAR22NF_week_0.parquet"))		
                    start_index = 787500
                    prefix = "NIFTY03MAR22"
                    text_file.write("For 03 MAR Expiry\n")

                if(xx == 190):
                    df=(pd.read_parquet(f"{path_nf_22}JAN_10MAR22NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY10MAR22"
                    text_file.write("For 10 MAR Expiry\n")

                if(xx == 191):
                    df=(pd.read_parquet(f"{path_nf_22}JAN_17MAR22NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY17MAR22"
                    text_file.write("For 17 MAR Expiry\n")

                if(xx == 192):
                    df=(pd.read_parquet(f"{path_nf_22}JAN_24MAR22NF_week_0.parquet"))		
                    start_index = 1125000
                    prefix = "NIFTY24MAR22"
                    text_file.write("For 24 MAR Expiry\n")
                
                if(xx == 193):
                    df=(pd.read_parquet(f"{path_nf_22}JAN_31MAR22NF_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "NIFTY31MAR22"
                    text_file.write("For 31 MAR Expiry\n")

                if(xx == 194):	
                    df=(pd.read_parquet(f"{path_nf_22}FEB_07APR22NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY07APR22"
                    text_file.write("For 7 April Expiry\n")

                if(xx == 195):		
                    df=(pd.read_parquet(f"{path_nf_22}FEB_13APR22NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY13APR22"
                    text_file.write("For 13 April Expiry\n")

                if(xx == 196):
                    df=(pd.read_parquet(f"{path_nf_22}FEB_21APR22NF_week_0.parquet"))		
                    start_index = 1147500
                    prefix = "NIFTY21APR22"
                    text_file.write("For 21 April Expiry\n")

                if(xx == 197):
                    df=(pd.read_parquet(f"{path_nf_22}FEB_28APR22NF_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "NIFTY28APR22"
                    text_file.write("For 28 April Expiry\n")

                if(xx == 198):	
                    df=(pd.read_parquet(f"{path_nf_22}MAR_05MAY22NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY05MAY22"
                    text_file.write("For 5 MAY Expiry\n")
                    
                if(xx == 199):		
                    df=(pd.read_parquet(f"{path_nf_22}MAR_12MAY22NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY12MAY22"
                    text_file.write("For 12 MAY Expiry\n")
                    
                if(xx == 200):	
                    df=(pd.read_parquet(f"{path_nf_22}MAR_19MAY22NF_week_0.parquet"))		
                    start_index = 1125000
                    prefix = "NIFTY19MAY22"
                    text_file.write("For 19 MAY Expiry\n")
                    
                if(xx == 201):	
                    df=(pd.read_parquet(f"{path_nf_22}MAR_26MAY22NF_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "NIFTY26MAY22"
                    text_file.write("For 26 MAY Expiry\n")	

                if(xx == 202):	
                    df=(pd.read_parquet(f"{path_nf_22}APR_02JUN22NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY02JUN22"
                    text_file.write("For 02 JUN Expiry\n")
                

                if(xx == 203):	
                    df=(pd.read_parquet(f"{path_nf_22}APR_09JUN22NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY09JUN22"
                    text_file.write("For 09 JUN Expiry\n")
                
                if(xx == 204):	
                    df=(pd.read_parquet(f"{path_nf_22}APR_16JUN22NF_week_0.parquet"))		
                    start_index = 1125000  
                    prefix = "NIFTY16JUN22"
                    text_file.write("For 16 JUN Expiry\n")
                
                if(xx == 205):	
                    df=(pd.read_parquet(f"{path_nf_22}APR_23JUN22NF_week_0.parquet"))		
                    start_index = 1237500 
                    prefix = "NIFTY23JUN22"
                    text_file.write("For 23 JUN Expiry\n")
                
                if(xx == 206):	
                    df=(pd.read_parquet(f"{path_nf_22}APR_30JUN22NF_week_0.parquet"))		
                    start_index = 1350000  
                    prefix = "NIFTY30JUN22"
                    text_file.write("For 30 JUN Expiry\n")

                if(xx == 207):	
                    df=(pd.read_parquet(f"{path_nf_22}MAY_07JUL22NF_week_0.parquet"))		
                    start_index = 900000  
                    prefix = "NIFTY07JUL22"
                    text_file.write("For 07 JUL Expiry\n")
                
                if(xx == 208):	
                    df=(pd.read_parquet(f"{path_nf_22}MAY_14JUL22NF_week_0.parquet"))		
                    start_index = 1012500  
                    prefix = "NIFTY14JUL22"
                    text_file.write("For 14 JUL Expiry\n")
                
                if(xx == 209):	
                    df=(pd.read_parquet(f"{path_nf_22}MAY_21JUL22NF_week_0.parquet"))		
                    start_index = 1125000   
                    prefix = "NIFTY21JUL22"
                    text_file.write("For 21 JUL Expiry\n")

                if(xx == 210):	
                    df=(pd.read_parquet(f"{path_nf_22}MAY_28JUL22NF_week_0.parquet"))		
                    start_index = 1237500    
                    prefix = "NIFTY28JUL22"
                    text_file.write("For 28 JUL Expiry\n")

                if(xx == 211):	
                    df=(pd.read_parquet(f"{path_nf_22}JUN_04AUG22NF_week_0.parquet"))		
                    start_index = 900000    
                    prefix = "NIFTY04AUG22"
                    text_file.write("For 04 AUG Expiry\n")
                
                if(xx == 212):	
                    df=(pd.read_parquet(f"{path_nf_22}JUN_11AUG22NF_week_0.parquet"))		
                    start_index = 1012500     
                    prefix = "NIFTY11AUG22"
                    text_file.write("For 11 AUG Expiry\n")

                if(xx == 213):	
                    df=(pd.read_parquet(f"{path_nf_22}JUN_18AUG22NF_week_0.parquet"))		
                    start_index = 1125000      
                    prefix = "NIFTY18AUG22"
                    text_file.write("For 18 AUG Expiry\n")
                
                if(xx == 214):	
                    df=(pd.read_parquet(f"{path_nf_22}JUN_25AUG22NF_week_0.parquet"))		
                    start_index = 1237500       
                    prefix = "NIFTY25AUG22"
                    text_file.write("For 25 AUG Expiry\n")

                if(xx == 215):	
                    df=(pd.read_parquet(f"{path_nf_22}JUL_01SEP22NF_week_0.parquet"))		
                    start_index = 900000    
                    prefix = "NIFTY01SEP22"
                    text_file.write("For 01 SEP Expiry\n")
                
                if(xx == 216):	
                    df=(pd.read_parquet(f"{path_nf_22}JUL_08SEP22NF_week_0.parquet"))		
                    start_index = 1012500      
                    prefix = "NIFTY08SEP22"
                    text_file.write("For 08 SEP Expiry\n")

                if(xx == 217):	
                    df=(pd.read_parquet(f"{path_nf_22}JUL_15SEP22NF_week_0.parquet"))		
                    start_index = 1125000       
                    prefix = "NIFTY15SEP22"
                    text_file.write("For 15 SEP Expiry\n")
                
                if(xx == 218):	
                    df=(pd.read_parquet(f"{path_nf_22}JUL_22SEP22NF_week_0.parquet"))		
                    start_index = 1237500        
                    prefix = "NIFTY22SEP22"
                    text_file.write("For 22 SEP Expiry\n")
                
                if(xx == 219):	
                    df=(pd.read_parquet(f"{path_nf_22}JUL_29SEP22NF_week_0.parquet"))	
                    start_index = 1350000        
                    prefix = "NIFTY29SEP22"
                    text_file.write("For 29 SEP Expiry\n")

                if(xx ==220):	
                    df=(pd.read_parquet(f"{path_nf_22}AUG_06OCT22NF_week_0.parquet"))		
                    start_index = 900000    
                    prefix = "NIFTY06OCT22"
                    text_file.write("For 06 OCT Expiry\n")
                
                if(xx == 221):	
                    df=(pd.read_parquet(f"{path_nf_22}AUG_13OCT22NF_week_0.parquet"))		
                    start_index = 1012500      
                    prefix = "NIFTY13OCT22"
                    text_file.write("For 13 OCT Expiry\n")

                if(xx == 222):	
                    df=(pd.read_parquet(f"{path_nf_22}AUG_20OCT22NF_week_0.parquet"))		
                    start_index = 1125000       
                    prefix = "NIFTY20OCT22"
                    text_file.write("For 20 OCT Expiry\n")
                
                if(xx == 223):	
                    df=(pd.read_parquet(f"{path_nf_22}AUG_27OCT22NF_week_0.parquet"))		
                    start_index = 1237500       
                    prefix = "NIFTY27OCT22"
                    text_file.write("For 27 OCT Expiry\n")

                if(xx == 224):	
                    df=(pd.read_parquet(f"{path_nf_22}SEP_03NOV22NF_week_0.parquet"))		
                    start_index = 900000    
                    prefix = "NIFTY03NOV22"
                    text_file.write("For 03 NOV Expiry\n")
                
                if(xx == 225):	
                    df=(pd.read_parquet(f"{path_nf_22}SEP_10NOV22NF_week_0.parquet"))		
                    start_index = 1012500      
                    prefix = "NIFTY10NOV22"
                    text_file.write("For 10 NOV Expiry\n")

                if(xx == 226):	
                    df=(pd.read_parquet(f"{path_nf_22}SEP_17NOV22NF_week_0.parquet"))		
                    start_index = 1125000       
                    prefix = "NIFTY17NOV22"
                    text_file.write("For 17 NOV Expiry\n")

                if(xx == 227):	
                    df=(pd.read_parquet(f"{path_nf_22}SEP_24NOV22NF_week_0.parquet"))		
                    start_index = 1237500       
                    prefix = "NIFTY24NOV22"
                    text_file.write("For 24 NOV Expiry\n")

                if(xx == 228):	
                    df=(pd.read_parquet(f"{path_nf_22}OCT_01DEC22NF_week_0.parquet"))		
                    start_index = 787500    
                    prefix = "NIFTY01DEC22"
                    text_file.write("For 01 DEC Expiry\n")

                if(xx == 229):	
                    df=(pd.read_parquet(f"{path_nf_22}OCT_08DEC22NF_week_0.parquet"))		
                    start_index = 900000      
                    prefix = "NIFTY08DEC22"
                    text_file.write("For 08 DEC Expiry\n")

                if(xx == 230):	
                    df=(pd.read_parquet(f"{path_nf_22}OCT_15DEC22NF_week_0.parquet"))		
                    start_index = 1012500       
                    prefix = "NIFTY15DEC22"
                    text_file.write("For 15 DEC Expiry\n")
                
                if(xx == 231):	
                    df=(pd.read_parquet(f"{path_nf_22}OCT_22DEC22NF_week_0.parquet"))		
                    start_index = 1125000       
                    prefix = "NIFTY22DEC22"
                    text_file.write("For 22 DEC Expiry\n")

                if(xx == 232):	
                    df=(pd.read_parquet(f"{path_nf_22}OCT_29DEC22NF_week_0.parquet"))		
                    start_index = 1237500        
                    prefix = "NIFTY29DEC22"
                    text_file.write("For 29 DEC Expiry\n")
                
                
                if(xx == 233):	
                    df=(pd.read_parquet(f"{path_nf_23}NOV_05JAN23NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY05JAN23"
                    text_file.write("For 5 JAN Expiry 23\n")
                    
                if(xx == 234):		
                    df=(pd.read_parquet(f"{path_nf_23}NOV_12JAN23NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY12JAN23"
                    text_file.write("For 12 JAN Expiry 23\n")
                    
                if(xx == 235):
                    df=(pd.read_parquet(f"{path_nf_23}NOV_19JAN23NF_week_0.parquet"))		
                    start_index = 1125000
                    prefix = "NIFTY19JAN23"
                    text_file.write("For 19 JAN Expiry 23\n")
                    
                if(xx == 236):
                    df=(pd.read_parquet(f"{path_nf_23}NOV_25JAN23NF_week_0.parquet"))		
                    start_index = 1575000
                    prefix = "NIFTY25JAN23"
                    text_file.write("For 25 JAN Expiry 23\n")
                
                if(xx == 237):	
                    df=(pd.read_parquet(f"{path_nf_23}DEC_02FEB23NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY02FEB23"
                    text_file.write("For 2 FEB Expiry 23\n")
                    
                if(xx == 238):		
                    df=(pd.read_parquet(f"{path_nf_23}DEC_09FEB23NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY09FEB23"
                    text_file.write("For 09 FEB Expiry 23\n")
                    
                if(xx == 239):
                    df=(pd.read_parquet(f"{path_nf_23}DEC_16FEB23NF_week_0.parquet"))		
                    start_index = 1125000
                    prefix = "NIFTY16FEB23"
                    text_file.write("For 16 FEB Expiry 23\n")
                
                if(xx == 240):
                    df=(pd.read_parquet(f"{path_nf_23}DEC_23FEB23NF_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "NIFTY23FEB23"
                    text_file.write("For 23 FEB Expiry 23\n")

                if(xx == 241):
                    df=(pd.read_parquet(f"{path_nf_23}06JAN_02MAR23NF_week_1.parquet"))		
                    start_index = 787500
                    prefix = "NIFTY02MAR23"
                    text_file.write("For 02 MAR Expiry 23\n")

                if(xx == 242):
                    df=(pd.read_parquet(f"{path_nf_23}06JAN_09MAR23NF_week_1.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY09MAR23"
                    text_file.write("For 09 MAR Expiry 23\n")

                if(xx == 243):
                    df=(pd.read_parquet(f"{path_nf_23}06JAN_16MAR23NF_week_1.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY16MAR23"
                    text_file.write("For 16 MAR Expiry 23\n")

                if(xx == 244):
                    df=(pd.read_parquet(f"{path_nf_23}06JAN_23MAR23NF_week_1.parquet"))		
                    start_index = 1125000  
                    prefix = "NIFTY23MAR23"
                    text_file.write("For 23 MAR Expiry 23\n")
                
                if(xx == 245):
                    df=(pd.read_parquet(f"{path_nf_23}06JAN_29MAR23NF_week_1.parquet"))		
                    start_index = 1237500  
                    prefix = "NIFTY29MAR23"
                    text_file.write("For 29 MAR Expiry\n")


                if(xx == 246):	
                    df=(pd.read_parquet(f"{path_nf_23}FEB_06APR23NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY06APR23"
                    text_file.write("For 6 April Expiry 23\n")

                if(xx == 247):		
                    df=(pd.read_parquet(f"{path_nf_23}FEB_13APR23NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY13APR23"
                    text_file.write("For 13 April Expiry 23\n")

                if(xx == 248):
                    df=(pd.read_parquet(f"{path_nf_23}FEB_20APR23NF_week_0.parquet"))		
                    start_index = 1147500
                    prefix = "NIFTY20APR23"
                    text_file.write("For 20 April Expiry 23\n")

                if(xx == 249):
                    df=(pd.read_parquet(f"{path_nf_23}FEB_27APR23NF_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "NIFTY27APR23"
                    text_file.write("For 27 April Expiry 23\n")

                if(xx == 250):	
                    df=(pd.read_parquet(f"{path_nf_23}MAR_04MAY23NF_week_0.parquet"))		
                    start_index = 900000
                    prefix = "NIFTY04MAY23"
                    text_file.write("For 4 MAY Expiry\n")
                    
                if(xx == 251):		
                    df=(pd.read_parquet(f"{path_nf_23}MAR_11MAY23NF_week_0.parquet"))		
                    start_index = 1012500
                    prefix = "NIFTY11MAY23"
                    text_file.write("For 11 MAY Expiry 23\n")
                    
                if(xx == 252):	
                    df=(pd.read_parquet(f"{path_nf_23}MAR_18MAY23NF_week_0.parquet"))		
                    start_index = 1125000
                    prefix = "NIFTY18MAY23"
                    text_file.write("For 18 MAY Expiry 23\n")
                    
                if(xx == 253):	
                    df=(pd.read_parquet(f"{path_nf_23}03MAR_25MAY23NF_week_0.parquet"))		
                    start_index = 1237500
                    prefix = "NIFTY25MAY23"
                    text_file.write("For 25 MAY Expiry\n")	

                if(xx == 254):	
                    df=(pd.read_parquet(f"{path_nf_23}APR_01JUN23NF_week_0.parquet"))		
                    start_index = 765000
                    prefix = "NIFTY01JUN23"
                    text_file.write("For 01 JUN Expiry 23\n")
                    
                if(xx == 255):	
                    df=(pd.read_parquet(f"{path_nf_23}APR_08JUN23NF_week_0.parquet"))		
                    start_index = 877500
                    prefix = "NIFTY08JUN23"
                    text_file.write("For 08 JUN Expiry 23\n")
                
                if(xx == 256):	
                    df=(pd.read_parquet(f"{path_nf_23}10APR_15JUN23NF_week_1.parquet"))		
                    start_index = 990000
                    prefix = "NIFTY15JUN23"
                    text_file.write("For 15 JUN Expiry 23\n")   
                
                
                if(xx==257):
                    df=(pd.read_parquet(f"{path_fnf_21}11AUG_19OCT21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY19OCT21" 
                    text_file.write("For 19 OCT Expiry\n")



                if(xx==258):
                    df=(pd.read_parquet(f"{path_fnf_21}11AUG_26OCT21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY26OCT21" 
                    text_file.write("For 26 OCT Expiry\n")

                

                if(xx==259):
                    df=(pd.read_parquet(f"{path_fnf_21}15SEP_02NOV21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY02NOV21" 
                    text_file.write("For 02 NOV Expiry\n")
                

                if(xx==260):
                    df=(pd.read_parquet(f"{path_fnf_21}15SEP_09NOV21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY09NOV21" 
                    text_file.write("For 09 NOV Expiry\n")

                

                if(xx==261):
                    df=(pd.read_parquet(f"{path_fnf_21}15SEP_16NOV21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY16NOV21" 
                    text_file.write("For 16 NOV Expiry\n")

                

                if(xx==262):
                    df=(pd.read_parquet(f"{path_fnf_21}15SEP_23NOV21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY23NOV21" 
                    text_file.write("For 23 NOV Expiry\n")

                
                if(xx==263):
                    df=(pd.read_parquet(f"{path_fnf_21}15SEP_30NOV21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY30NOV21" 
                    text_file.write("For 30 NOV Expiry\n")

                

                if(xx==264):
                    df=(pd.read_parquet(f"{path_fnf_21}13OCT_07DEC21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY07DEC21" 
                    text_file.write("For 07 DEC Expiry\n")

                

                if(xx==265):
                    df=(pd.read_parquet(f"{path_fnf_21}13OCT_14DEC21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY14DEC21" 
                    text_file.write("For 14 DEC Expiry\n")

                

                if(xx==266):
                    df=(pd.read_parquet(f"{path_fnf_21}13OCT_21DEC21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY21DEC21" 
                    text_file.write("For 21 DEC Expiry\n")

                

                if(xx==267):
                    df=(pd.read_parquet(f"{path_fnf_21}13OCT_28DEC21FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY28DEC21" 
                    text_file.write("For 28 DEC Expiry\n")

                

                if(xx==268):
                    df=(pd.read_parquet(f"{path_fnf_22}16NOV_04JAN22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY04JAN22" 
                    text_file.write("For 04 JAN Expiry\n")

                

                if(xx==269):
                    df=(pd.read_parquet(f"{path_fnf_22}16NOV_11JAN22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY11JAN22" 
                    text_file.write("For 11 JAN Expiry\n")

                

                if(xx==270):
                    df=(pd.read_parquet(f"{path_fnf_22}16NOV_18JAN22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY18JAN22" 
                    text_file.write("For 18 JAN Expiry\n")

                

                if(xx==271):
                    df=(pd.read_parquet(f"{path_fnf_22}16NOV_25JAN22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY25JAN22" 
                    text_file.write("For 25 JAN Expiry\n")

                

                if(xx==272):
                    df=(pd.read_parquet(f"{path_fnf_22}14DEC_01FEB22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY01FEB22" 
                    text_file.write("For 01 FEB Expiry\n")

                

                if(xx==273):
                    df=(pd.read_parquet(f"{path_fnf_22}14DEC_08FEB22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY08FEB22" 
                    text_file.write("For 08 FEB Expiry\n")

                

                if(xx==274):
                    df=(pd.read_parquet(f"{path_fnf_22}14DEC_15FEB22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY08FEB22" 
                    text_file.write("For 15 FEB Expiry\n")

                

                if(xx==275):
                    df=(pd.read_parquet(f"{path_fnf_22}14DEC_22FEB22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY22FEB22" 
                    text_file.write("For 22 FEB Expiry\n")

                

                if(xx==276):
                    df=(pd.read_parquet(f"{path_fnf_22}14DEC_28FEB22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY28FEB22" 
                    text_file.write("For 28 FEB Expiry\n")

                

                if(xx==277):
                    df=(pd.read_parquet(f"{path_fnf_22}18JAN_08MAR22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY08MAR22" 
                    text_file.write("For 08 MAR Expiry\n")

                

                if(xx==278):
                    df=(pd.read_parquet(f"{path_fnf_22}18JAN_15MAR22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY15MAR22" 
                    text_file.write("For 15 MAR Expiry\n")

                

                if(xx==279):
                    df=(pd.read_parquet(f"{path_fnf_22}18JAN_22MAR22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY22MAR22" 
                    text_file.write("For 22 MAR Expiry\n")

                

                if(xx==280):
                    df=(pd.read_parquet(f"{path_fnf_22}18JAN_29MAR22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY29MAR22" 
                    text_file.write("For 29 MAR Expiry\n")

                

                if(xx==281):
                    df=(pd.read_parquet(f"{path_fnf_22}15FEB_05APR22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY05APR22" 
                    text_file.write("For 05 APR Expiry\n")

                

                if(xx==282):
                    df=(pd.read_parquet(f"{path_fnf_22}15FEB_12APR22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY12APR22" 
                    text_file.write("For 12 APR Expiry\n")

                

                if(xx==283):
                    df=(pd.read_parquet(f"{path_fnf_22}15FEB_19APR22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY19APR22" 
                    text_file.write("For 19 APR Expiry\n")

                
                if(xx==284):
                    df=(pd.read_parquet(f"{path_fnf_22}15FEB_26APR22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY26APR22" 
                    text_file.write("For 26 APR Expiry\n")

                

                if(xx==285):
                    df=(pd.read_parquet(f"{path_fnf_22}07MAR_02MAY22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY02MAY22" 
                    text_file.write("For 02 MAY Expiry\n")

                

                if(xx==286):
                    df=(pd.read_parquet(f"{path_fnf_22}07MAR_10MAY22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY10MAY22" 
                    text_file.write("For 10 MAY Expiry\n")

                

                if(xx==287):
                    df=(pd.read_parquet(f"{path_fnf_22}07MAR_17MAY22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY17MAY22" 
                    text_file.write("For 17 MAY Expiry\n")

                

                if(xx==288):
                    df=(pd.read_parquet(f"{path_fnf_22}07MAR_24MAY22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY24MAY22" 
                    text_file.write("For 24 MAY Expiry\n")

                

                if(xx==289):
                    df=(pd.read_parquet(f"{path_fnf_22}07MAR_31MAY22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY31MAY22" 
                    text_file.write("For 31 MAY Expiry\n")

                

                if(xx==290):
                    df=(pd.read_parquet(f"{path_fnf_22}06APR_07JUN22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY07JUN22" 
                    text_file.write("For 07 JUN Expiry\n")

                

                if(xx==291):
                    df=(pd.read_parquet(f"{path_fnf_22}06APR_14JUN22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY14JUN22" 
                    text_file.write("For 14 JUN Expiry\n")

                

                if(xx==292):
                    df=(pd.read_parquet(f"{path_fnf_22}06APR_21JUN22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY21JUN22" 
                    text_file.write("For 21 JUN Expiry\n")

                

                if(xx==293):
                    df=(pd.read_parquet(f"{path_fnf_22}06APR_28JUN22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY28JUN22" 
                    text_file.write("For 28 JUN Expiry\n")

                

                if(xx==294):
                    df=(pd.read_parquet(f"{path_fnf_22}11MAY_05JUL22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY01JUL22" 
                    text_file.write("For 05 JUL Expiry\n")

                

                if(xx==295):
                    df=(pd.read_parquet(f"{path_fnf_22}11MAY_12JUL22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY12JUL22" 
                    text_file.write("For 12 JUL Expiry\n")

                

                if(xx==296):
                    df=(pd.read_parquet(f"{path_fnf_22}11MAY_19JUL22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY19JUL22" 
                    text_file.write("For 19 JUL Expiry\n")

                

                if(xx==297):
                    df=(pd.read_parquet(f"{path_fnf_22}11MAY_26JUL22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY26JUL22" 
                    text_file.write("For 26 JUL Expiry\n")

                

                if(xx==298):
                    df=(pd.read_parquet(f"{path_fnf_22}11MAY_02AUG22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY02AUG22" 
                    text_file.write("For 02 AUG Expiry\n")

                
                if(xx==299):
                    df=(pd.read_parquet(f"{path_fnf_22}08JUN_08AUG22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY08AUG22" 
                    text_file.write("For 08 AUG Expiry\n")

                

                if(xx==300):
                    df=(pd.read_parquet(f"{path_fnf_22}08JUN_16AUG22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY16AUG22" 
                    text_file.write("For 16 AUG Expiry\n")

                

                if(xx==301):
                    df=(pd.read_parquet(f"{path_fnf_22}08JUN_23AUG22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY23AUG22" 
                    text_file.write("For 23 AUG Expiry\n")

                

                if(xx==302):
                    df=(pd.read_parquet(f"{path_fnf_22}08JUN_30AUG22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY30AUG22" 
                    text_file.write("For 30 AUG Expiry\n")

                

                if(xx==303):
                    df=(pd.read_parquet(f"{path_fnf_22}06JUL_06SEP22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY06SEP22" 
                    text_file.write("For 06 SEP Expiry\n")

                

                if(xx==304):
                    df=(pd.read_parquet(f"{path_fnf_22}06JUL_13SEP22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY13SEP22" 
                    text_file.write("For 13 SEP Expiry\n")

                

                if(xx==305):
                    df=(pd.read_parquet(f"{path_fnf_22}06JUL_20SEP22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY20SEP22" 
                    text_file.write("For 20 SEP Expiry\n")

                

                if(xx==306):
                    df=(pd.read_parquet(f"{path_fnf_22}06JUL_27SEP22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY27SEP22" 
                    text_file.write("For 27 SEP Expiry\n")

                

                if(xx==307):
                    df=(pd.read_parquet(f"{path_fnf_22}03AUG_04OCT22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY04OCT22" 
                    text_file.write("For 04 OCT Expiry\n")

                

                if(xx==308):
                    df=(pd.read_parquet(f"{path_fnf_22}03AUG_11OCT22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY11OCT22" 
                    text_file.write("For 11 OCT Expiry\n")

                

                if(xx==309):
                    df=(pd.read_parquet(f"{path_fnf_22}03AUG_18OCT22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY18OCT22" 
                    text_file.write("For 18 OCT Expiry\n")

                
                if(xx==310):
                    df=(pd.read_parquet(f"{path_fnf_22}03AUG_25OCT22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY25OCT22" 
                    text_file.write("For 25 OCT Expiry\n")

                

                if(xx==311):
                    df=(pd.read_parquet(f"{path_fnf_22}07SEP_01NOV22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY01NOV22" 
                    text_file.write("For 01 NOV Expiry\n")

                

                if(xx==312):
                    df=(pd.read_parquet(f"{path_fnf_22}07SEP_07NOV22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY07NOV22" 
                    text_file.write("For 07 NOV Expiry\n")

                

                if(xx==313):
                    df=(pd.read_parquet(f"{path_fnf_22}07SEP_15NOV22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY15NOV22" 
                    text_file.write("For 15 NOV Expiry\n")

                

                if(xx==314):
                    df=(pd.read_parquet(f"{path_fnf_22}07SEP_22NOV22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY22NOV22" 
                    text_file.write("For 22 NOV Expiry\n")

                

                if(xx==315):
                    df=(pd.read_parquet(f"{path_fnf_22}07SEP_29NOV22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY29NOV22" 
                    text_file.write("For 29 NOV Expiry\n")

                

                if(xx==316):
                    df=(pd.read_parquet(f"{path_fnf_22}06OCT_06DEC22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY06DEC22" 
                    text_file.write("For 06 DEC Expiry\n")

                

                if(xx==317):
                    df=(pd.read_parquet(f"{path_fnf_22}06OCT_13DEC22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY13DEC22" 
                    text_file.write("For 13 DEC Expiry\n")

                

                if(xx==318):
                    df=(pd.read_parquet(f"{path_fnf_22}06OCT_20DEC22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY20DEC22" 
                    text_file.write("For 20 DEC Expiry\n")

                

                if(xx==319):
                    df=(pd.read_parquet(f"{path_fnf_22}06OCT_27DEC22FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY27DEC22" 
                    text_file.write("For 27 DEC Expiry\n")

                if(xx==320):
                    df=(pd.read_parquet(f"{path_fnf_23}01NOV_03JAN23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY03JAN23" 
                    text_file.write("For 03 JAN Expiry\n")



                if(xx==321):
                    df=(pd.read_parquet(f"{path_fnf_23}01NOV_10JAN23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY10JAN23" 
                    text_file.write("For 10 JAN Expiry\n")



                if(xx==322):
                    df=(pd.read_parquet(f"{path_fnf_23}01NOV_17JAN23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY17JAN23" 
                    text_file.write("For 17 JAN Expiry\n")



                if(xx==323):
                    df=(pd.read_parquet(f"{path_fnf_23}01NOV_24JAN23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY24JAN23" 
                    text_file.write("For 24 JAN Expiry\n")



                if(xx==324):
                    df=(pd.read_parquet(f"{path_fnf_23}01NOV_31JAN23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY31JAN23" 
                    text_file.write("For 31 JAN Expiry\n")



                if(xx==325):
                    df=(pd.read_parquet(f"{path_fnf_23}06DEC_07FEB23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY07FEB23" 
                    text_file.write("For 07 FEB Expiry\n")



                if(xx==326):
                    df=(pd.read_parquet(f"{path_fnf_23}06DEC_14FEB23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY14FEB23" 
                    text_file.write("For 14 FEB Expiry\n")



                if(xx==327):
                    df=(pd.read_parquet(f"{path_fnf_23}06DEC_21FEB23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY21FEB23" 
                    text_file.write("For 21 FEB Expiry\n")



                if(xx==328):
                    df=(pd.read_parquet(f"{path_fnf_23}06DEC_28FEB23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY28FEB23" 
                    text_file.write("For 28 FEB Expiry\n")



                if(xx==329):
                    df=(pd.read_parquet(f"{path_fnf_23}03JAN_06MAR23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY06MAR23" 
                    text_file.write("For 06 MAR Expiry\n")



                if(xx==330):
                    df=(pd.read_parquet(f"{path_fnf_23}03JAN_14MAR23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY14MAR23" 
                    text_file.write("For 14 MAR Expiry\n")


                if(xx==331):
                    df=(pd.read_parquet(f"{path_fnf_23}03JAN_21MAR23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY21MAR23" 
                    text_file.write("For 21 MAR Expiry\n")



                if(xx==332):
                    df=(pd.read_parquet(f"{path_fnf_23}03JAN_28MAR23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY28MAR23" 
                    text_file.write("For 28 MAR Expiry\n")



                if(xx==333):
                    df=(pd.read_parquet(f"{path_fnf_23}07FEB_03APR23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY03APR23" 
                    text_file.write("For 03 APR Expiry\n")


                if(xx==334):
                    df=(pd.read_parquet(f"{path_fnf_23}07FEB_11APR23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY11APR23" 
                    text_file.write("For 11 APR Expiry\n")



                if(xx==335):
                    df=(pd.read_parquet(f"{path_fnf_23}07FEB_18APR23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY18APR23" 
                    text_file.write("For 18 APR Expiry\n")



                if(xx==336):
                    df=(pd.read_parquet(f"{path_fnf_23}07FEB_25APR23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY25APR23" 
                    text_file.write("For 25 APR Expiry\n")



                if(xx==337):
                    df=(pd.read_parquet(f"{path_fnf_23}06MAR_02MAY23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY02MAY23" 
                    text_file.write("For 02 MAY Expiry\n")



                if(xx==338):
                    df=(pd.read_parquet(f"{path_fnf_23}06MAR_09MAY23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY09MAY23" 
                    text_file.write("For 09 MAY Expiry\n")



                if(xx==339):
                    df=(pd.read_parquet(f"{path_fnf_23}06MAR_16MAY23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY16MAY23" 
                    text_file.write("For 16 MAY Expiry\n")



                if(xx==340):
                    df=(pd.read_parquet(f"{path_fnf_23}06MAR_23MAY23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY23MAY23" 
                    text_file.write("For 23 MAY Expiry\n")



                if(xx==341):
                    df=(pd.read_parquet(f"{path_fnf_23}06MAR_30MAY23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY30MAY23" 
                    text_file.write("For 30 MAY Expiry\n")



                if(xx==342):
                    df=(pd.read_parquet(f"{path_fnf_23}03APR_06JUN23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY06JUN23" 
                    text_file.write("For 06 JUN Expiry\n")



                if(xx==343):
                    df=(pd.read_parquet(f"{path_fnf_23}03APR_13JUN23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY13JUN23" 
                    text_file.write("For 13 JUN Expiry\n")



                if(xx==344):
                    df=(pd.read_parquet(f"{path_fnf_23}03APR_20JUN23FNF_week_0.parquet")) 
                    start_index = 0 
                    prefix = "FINNIFTY20JUN23" 
                    text_file.write("For 20 JUN Expiry\n")

                


                
                total_pnl,trading_days, cummulative_trade, profit, winning_days, loss, lossing_days, winning_trades,\
                    lossing_trades, winning_trades, tradepnl, SL_count, mis_count,expiry,par,monday_pnl_2022,tuesday_pnl_2022,wednesday_pnl_2022,\
                    thursday_pnl_2022,friday_pnl_2022,jan_pnl_2022,feb_pnl_2022,mar_pnl_2022,apr_pnl_2022,may_pnl_2022,jun_pnl_2022,jul_pnl_2022,aug_pnl_2022,sep_pnl_2022,oct_pnl_2022,nov_pnl_2022,dec_pnl_2022,monday_pnl_2023,tuesday_pnl_2023,wednesday_pnl_2023,\
                    thursday_pnl_2023,friday_pnl_2023,jan_pnl_2023,feb_pnl_2023,mar_pnl_2023,apr_pnl_2023,may_pnl_2023,jun_pnl_2023,jul_pnl_2023,aug_pnl_2023,sep_pnl_2023,oct_pnl_2023,nov_pnl_2023,dec_pnl_2023,monday_pnl_2021,tuesday_pnl_2021,wednesday_pnl_2021,thursday_pnl_2021,friday_pnl_2021,jan_pnl_2021,feb_pnl_2021,mar_pnl_2021,apr_pnl_2021,may_pnl_2021,jun_pnl_2021,jul_pnl_2021,aug_pnl_2021,sep_pnl_2021,oct_pnl_2021,nov_pnl_2021,dec_pnl_2021,monday_pnl_2020,tuesday_pnl_2020,wednesday_pnl_2020,thursday_pnl_2020,friday_pnl_2020,jan_pnl_2020,feb_pnl_2020,mar_pnl_2020,apr_pnl_2020,may_pnl_2020,jun_pnl_2020,jul_pnl_2020,aug_pnl_2020,sep_pnl_2020,oct_pnl_2020,nov_pnl_2020,dec_pnl_2020,monday_pnl_2019,tuesday_pnl_2019,wednesday_pnl_2019,thursday_pnl_2019,friday_pnl_2019,jan_pnl_2019,feb_pnl_2019,mar_pnl_2019,apr_pnl_2019,may_pnl_2019,jun_pnl_2019,jul_pnl_2019,aug_pnl_2019,sep_pnl_2019,oct_pnl_2019,nov_pnl_2019,dec_pnl_2019, monday_pnl_2018,tuesday_pnl_2018,wednesday_pnl_2018,thursday_pnl_2018,friday_pnl_2018,jan_pnl_2018,feb_pnl_2018,mar_pnl_2018,apr_pnl_2018,may_pnl_2018,jun_pnl_2018,jul_pnl_2018,aug_pnl_2018,sep_pnl_2018,oct_pnl_2018,nov_pnl_2018,dec_pnl_2018=backtest(df,prefix,start_index)


        #all the calculations are done below
        # if trading_days == 0 or cummulative_trade == 0 or winning_days

        def calculate_ratio(numerator, denominator):
            try:
                result = float(numerator / denominator)
                return float(format(result, '.2f'))
            except ZeroDivisionError:
                return 0

        # Calculate ratios
        pnl_perday = calculate_ratio(total_pnl, trading_days)
        pnl_pertrade = calculate_ratio(total_pnl, cummulative_trade)
        avg_profit_winning_days = calculate_ratio(profit, winning_days)
        avg_loss_lossing_days = calculate_ratio(loss, lossing_days)
        avg_profit_winning_trades = calculate_ratio(profit, winning_trades)
        avg_loss_lossing_trades = calculate_ratio(loss, lossing_trades)

        # Avoid division by zero for ratios involving percentages
        daywise_accuracy = calculate_ratio((winning_days / trading_days) * 100, 1)
        tradewise_accuracy = calculate_ratio((winning_trades / cummulative_trade) * 100, 1)


        # pnl_perday=format(float(total_pnl/trading_days),'.2f')
        # pnl_pertrade=format(float(total_pnl/cummulative_trade),'.2f')
        # avg_profit_winning_days=float(format(profit/winning_days,'.2f'))
        # avg_loss_lossing_days=float(format(loss/lossing_days,'.2f'))
        # avg_profit_winning_trades=float(format(profit/winning_trades,'.2f'))
        # avg_loss_lossing_trades=float(format(loss/lossing_trades,'.2f'))
        # max_t=float(format(max(dpnl.values()),'.2f'))
        # max_t=float(format(loss/lossing_days,'.2f'))
        # # max_tk=max(dpnl, key=dpnl.get)
        # min_t=float(format(min(dpnl.values()),'.2f'))
        # # min_tk=min(dpnl, key=dpnl.get)
        # daywise_accuracy=float(format((winning_days/trading_days)*100,'.2f'))
        # tradewise_accuracy=float(format((winning_trades/cummulative_trade)*100,'.2f'))
        par=np.array(par)
        # text_file.write(temp_99)


        # print(dff2)

        # df123.to_csv("sdsdsd.csv")
        # text_file.write(df123)
        # if par[par>0]==[]:
        #     par.append(0)
        # text_file.write(par[par>0])
        # text_file.write("-----------------------------------`")
        # text_file.write(len(trade_day), 'day')
        # text_file.write(len(trade_dt), 'date')
        # text_file.write(len(trade_exp), 'Expiry')
        # text_file.write(len(trade_typel), 'tradetype')
        # text_file.write(len(instrument), 'instrument')
        # text_file.write(len(entry_t), 'entrytime')
        # text_file.write(len(entry_p), 'entrypremium')
        # text_file.write(len(exit_t), 'exittime')
        # text_file.write(len(exit_p), 'exit_premium')
        # text_file.write(len(tradepnl), 'PNL')
        # text_file.write(len(max_run_up_profit), 'Max unrealised Profit during whole trade')
        # text_file.write(len(max_run_up_loss), 'Max unrealised loss during whole trade')
        # text_file.write("-----------------------------------`")
        # text_file.write("-----------------------------------`")
        # text_file.write((trade_day), 'day')
        # text_file.write((trade_dt), 'date')
        # text_file.write((trade_exp), 'Expiry')
        # text_file.write((trade_typel), 'tradetype')
        # text_file.write((instrument), 'instrument')
        # text_file.write((entry_t), 'entrytime')
        # text_file.write((entry_p), 'entrypremium')
        # text_file.write((exit_t), 'exittime')
        # text_file.write((exit_p), 'exit_premium')
        # text_file.write((tradepnl), 'PNL')
        # text_file.write((max_run_up_profit), 'Max unrealised Profit during whole trade')
        # text_file.write((max_run_up_loss), 'Max unrealised loss during whole trade')

        
        counter=defaultdict(list)
        for key,val in groupby(par,lambda x: "plus" if x>0 else "minus"):
            counter[key].append(len(list(val)))
        res=[]
        for key in ('plus','minus'):
            res.append(counter[key])


        dar.extend(tradepnl)
        counter=defaultdict(list)
        for key,val in groupby(dar,lambda y: "plus" if y>0 else "minus"):
            counter[key].append(len(list(val)))
        des=[]
        for key in ('plus','minus'):
            des.append(counter[key])
        max_t=float(format(max(par),'.2f'))
        min_t=float(format(min(par),'.2f'))
        max_tt=float(format(max(tradepnl),'.2f'))
        min_tt=float(format(min(tradepnl),'.2f'))

        # per_change_monday=float(format(100*((monday_pnl-friday_pnl)/friday_pnl),'.2f'))
        # per_change_tuesday=float(format(100*((tuesday_pnl-monday_pnl)/monday_pnl),'.2f'))
        # per_change_wednesday=float(format(100*((wednesday_pnl-tuesday_pnl)/tuesday_pnl),'.2f'))
        # per_change_thursday=float(format(100*((thursday_pnl-wednesday_pnl)/wednesday_pnl),'.2f'))
        # per_change_friday=float(format(100*((friday_pnl-thursday_pnl)/thursday_pnl),'.2f'))


        # per_change_feb=float(format(100*((feb_pnl-jan_pnl)/jan_pnl),'.2f'))
        # per_change_mar=float(format(100*((mar_pnl-feb_pnl)/feb_pnl),'.2f'))
        # per_change_apr=float(format(100*((apr_pnl-mar_pnl)/mar_pnl),'.2f'))
        # per_change_may=float(format(100*((may_pnl-apr_pnl)/apr_pnl),'.2f'))
        # per_change_jun=float(format(100*((jun_pnl-may_pnl)/may_pnl),'.2f'))
        # per_change_jul=float(format(100*((jul_pnl-jun_pnl)/jun_pnl),'.2f'))
        # per_change_aug=float(format(100*((aug_pnl-jul_pnl)/jul_pnl),'.2f'))
        # per_change_sep=float(format(100*((sep_pnl-aug_pnl)/aug_pnl),'.2f'))
        # per_change_oct=float(format(100*((oct_pnl-sep_pnl)/sep_pnl),'.2f'))
        # per_change_nov=float(format(100*((nov_pnl-oct_pnl)/oct_pnl),'.2f'))
        # per_change_dec=float(format(100*((dec_pnl-nov_pnl)/nov_pnl),'.2f'))
        rounded_total_pnl = float(format((total_pnl),'.2f'))
        rounded_loss = float(format((loss),'.2f'))

        rounded_monday_pnl_2018 = float(format(monday_pnl_2018, '.2f'))
        rounded_tuesday_pnl_2018 = float(format(tuesday_pnl_2018, '.2f'))
        rounded_wednesday_pnl_2018 = float(format(wednesday_pnl_2018, '.2f'))
        rounded_thursday_pnl_2018 = float(format(thursday_pnl_2018, '.2f'))
        rounded_friday_pnl_2018 = float(format(friday_pnl_2018, '.2f'))

        rounded_monday_pnl_2019 = float(format(monday_pnl_2019, '.2f'))
        rounded_tuesday_pnl_2019 = float(format(tuesday_pnl_2019, '.2f'))
        rounded_wednesday_pnl_2019 = float(format(wednesday_pnl_2019, '.2f'))
        rounded_thursday_pnl_2019 = float(format(thursday_pnl_2019, '.2f'))
        rounded_friday_pnl_2019 = float(format(friday_pnl_2019, '.2f'))

        rounded_monday_pnl_2020 = float(format(monday_pnl_2020, '.2f'))
        rounded_tuesday_pnl_2020 = float(format(tuesday_pnl_2020, '.2f'))
        rounded_wednesday_pnl_2020 = float(format(wednesday_pnl_2020, '.2f'))
        rounded_thursday_pnl_2020 = float(format(thursday_pnl_2020, '.2f'))
        rounded_friday_pnl_2020 = float(format(friday_pnl_2020, '.2f'))
            
        rounded_monday_pnl_2021 = float(format(monday_pnl_2021, '.2f'))
        rounded_tuesday_pnl_2021 = float(format(tuesday_pnl_2021, '.2f'))
        rounded_wednesday_pnl_2021 = float(format(wednesday_pnl_2021, '.2f'))
        rounded_thursday_pnl_2021 = float(format(thursday_pnl_2021, '.2f'))
        rounded_friday_pnl_2021 = float(format(friday_pnl_2021, '.2f'))
        
        rounded_monday_pnl_2022 = float(format(monday_pnl_2022, '.2f'))
        rounded_tuesday_pnl_2022 = float(format(tuesday_pnl_2022, '.2f'))
        rounded_wednesday_pnl_2022 = float(format(wednesday_pnl_2022, '.2f'))
        rounded_thursday_pnl_2022 = float(format(thursday_pnl_2022, '.2f'))
        rounded_friday_pnl_2022 = float(format(friday_pnl_2022, '.2f'))
        
        rounded_monday_pnl_2023 = float(format(monday_pnl_2023, '.2f'))
        rounded_tuesday_pnl_2023 = float(format(tuesday_pnl_2023, '.2f'))
        rounded_wednesday_pnl_2023 = float(format(wednesday_pnl_2023, '.2f'))
        rounded_thursday_pnl_2023 = float(format(thursday_pnl_2023, '.2f'))
        rounded_friday_pnl_2023 = float(format(friday_pnl_2023, '.2f'))

        rounded_jan_pnl_2018 = float(format(jan_pnl_2018, '.2f'))
        rounded_feb_pnl_2018 = float(format(feb_pnl_2018, '.2f'))
        rounded_mar_pnl_2018 = float(format(mar_pnl_2018, '.2f'))
        rounded_apr_pnl_2018 = float(format(apr_pnl_2018, '.2f'))
        rounded_may_pnl_2018 = float(format(may_pnl_2018, '.2f'))
        rounded_jun_pnl_2018 = float(format(jun_pnl_2018, '.2f'))
        rounded_jul_pnl_2018 = float(format(jul_pnl_2018, '.2f'))
        rounded_aug_pnl_2018 = float(format(aug_pnl_2018, '.2f'))
        rounded_sep_pnl_2018 = float(format(sep_pnl_2018, '.2f'))
        rounded_oct_pnl_2018 = float(format(oct_pnl_2018, '.2f'))
        rounded_nov_pnl_2018 = float(format(nov_pnl_2018, '.2f'))
        rounded_dec_pnl_2018 = float(format(dec_pnl_2018, '.2f'))

        rounded_jan_pnl_2019 = float(format(jan_pnl_2019, '.2f'))
        rounded_feb_pnl_2019 = float(format(feb_pnl_2019, '.2f'))
        rounded_mar_pnl_2019 = float(format(mar_pnl_2019, '.2f'))
        rounded_apr_pnl_2019 = float(format(apr_pnl_2019, '.2f'))
        rounded_may_pnl_2019 = float(format(may_pnl_2019, '.2f'))
        rounded_jun_pnl_2019 = float(format(jun_pnl_2019, '.2f'))
        rounded_jul_pnl_2019 = float(format(jul_pnl_2019, '.2f'))
        rounded_aug_pnl_2019 = float(format(aug_pnl_2019, '.2f'))
        rounded_sep_pnl_2019 = float(format(sep_pnl_2019, '.2f'))
        rounded_oct_pnl_2019 = float(format(oct_pnl_2019, '.2f'))
        rounded_nov_pnl_2019 = float(format(nov_pnl_2019, '.2f'))
        rounded_dec_pnl_2019 = float(format(dec_pnl_2019, '.2f'))        

        rounded_jan_pnl_2020 = float(format(jan_pnl_2020, '.2f'))
        rounded_feb_pnl_2020 = float(format(feb_pnl_2020, '.2f'))
        rounded_mar_pnl_2020 = float(format(mar_pnl_2020, '.2f'))
        rounded_apr_pnl_2020 = float(format(apr_pnl_2020, '.2f'))
        rounded_may_pnl_2020 = float(format(may_pnl_2020, '.2f'))
        rounded_jun_pnl_2020 = float(format(jun_pnl_2020, '.2f'))
        rounded_jul_pnl_2020 = float(format(jul_pnl_2020, '.2f'))
        rounded_aug_pnl_2020 = float(format(aug_pnl_2020, '.2f'))
        rounded_sep_pnl_2020 = float(format(sep_pnl_2020, '.2f'))
        rounded_oct_pnl_2020 = float(format(oct_pnl_2020, '.2f'))
        rounded_nov_pnl_2020 = float(format(nov_pnl_2020, '.2f'))
        rounded_dec_pnl_2020 = float(format(dec_pnl_2020, '.2f'))

        rounded_jan_pnl_2021 = float(format(jan_pnl_2021, '.2f'))
        rounded_feb_pnl_2021 = float(format(feb_pnl_2021, '.2f'))
        rounded_mar_pnl_2021 = float(format(mar_pnl_2021, '.2f'))
        rounded_apr_pnl_2021 = float(format(apr_pnl_2021, '.2f'))
        rounded_may_pnl_2021 = float(format(may_pnl_2021, '.2f'))
        rounded_jun_pnl_2021 = float(format(jun_pnl_2021, '.2f'))
        rounded_jul_pnl_2021 = float(format(jul_pnl_2021, '.2f'))
        rounded_aug_pnl_2021 = float(format(aug_pnl_2021, '.2f'))
        rounded_sep_pnl_2021 = float(format(sep_pnl_2021, '.2f'))
        rounded_oct_pnl_2021 = float(format(oct_pnl_2021, '.2f'))
        rounded_nov_pnl_2021 = float(format(nov_pnl_2021, '.2f'))
        rounded_dec_pnl_2021 = float(format(dec_pnl_2021, '.2f'))

        rounded_jan_pnl_2022 = float(format(jan_pnl_2022, '.2f'))
        rounded_feb_pnl_2022 = float(format(feb_pnl_2022, '.2f'))
        rounded_mar_pnl_2022 = float(format(mar_pnl_2022, '.2f'))
        rounded_apr_pnl_2022 = float(format(apr_pnl_2022, '.2f'))
        rounded_may_pnl_2022 = float(format(may_pnl_2022, '.2f'))
        rounded_jun_pnl_2022 = float(format(jun_pnl_2022, '.2f'))
        rounded_jul_pnl_2022 = float(format(jul_pnl_2022, '.2f'))
        rounded_aug_pnl_2022 = float(format(aug_pnl_2022, '.2f'))
        rounded_sep_pnl_2022 = float(format(sep_pnl_2022, '.2f'))
        rounded_oct_pnl_2022 = float(format(oct_pnl_2022, '.2f'))
        rounded_nov_pnl_2022 = float(format(nov_pnl_2022, '.2f'))
        rounded_dec_pnl_2022 = float(format(dec_pnl_2022, '.2f'))
        
        rounded_jan_pnl_2023 = float(format(jan_pnl_2023, '.2f'))
        rounded_feb_pnl_2023 = float(format(feb_pnl_2023, '.2f'))
        rounded_mar_pnl_2023 = float(format(mar_pnl_2023, '.2f'))
        rounded_apr_pnl_2023 = float(format(apr_pnl_2023, '.2f'))
        rounded_may_pnl_2023 = float(format(may_pnl_2023, '.2f'))
        rounded_jun_pnl_2023 = float(format(jun_pnl_2023, '.2f'))
        rounded_jul_pnl_2023 = float(format(jul_pnl_2023, '.2f'))
        rounded_aug_pnl_2023 = float(format(aug_pnl_2023, '.2f'))
        rounded_sep_pnl_2023 = float(format(sep_pnl_2023, '.2f'))
        rounded_oct_pnl_2023 = float(format(oct_pnl_2023, '.2f'))
        rounded_nov_pnl_2023 = float(format(nov_pnl_2023, '.2f'))
        rounded_dec_pnl_2023 = float(format(dec_pnl_2023, '.2f'))

        text_file.write('********************************************#####################************************************************\n')  
        text_file.write(f'                                                                      CALCULATIONS ')
        text_file.write('\n')         
        text_file.write(f"Total PNL: {rounded_total_pnl}\n")
        text_file.write(f"Total Trades: {cummulative_trade}\n")
        text_file.write(f"Total Trade Days: {trading_days}\n")
        text_file.write(f"Profit: {profit}\n")
        text_file.write(f"Loss: {rounded_loss}\n")
        text_file.write(f"PNL Per Day: {pnl_perday}\n")
        text_file.write(f"PNL Per Trade: {pnl_pertrade}\n")

        # text_file.write(res)
        # text_file.write(des)

        if res[0]==[]:
            res[0]=[0]
        if res[1]==[]:
            res[1]=[0]

        if des[0]==[]:
            des[0]=[0]
        if des[1]==[]:
            des[1]=[0]


        text_file.write(f"Winning Streak: {str(max(res[0]))}\n")
        win_strk=str(max(res[0]))
        text_file.write(f"Losing Streak: {str(max(res[1]))}\n")
        lose_strk=str(max(res[1]))
        text_file.write(f"Winning Streak Trade: {str(max(des[0]))}\n")
        win_strk_t=str(max(des[0]))
        text_file.write(f"Losing Streak Trade: {str(max(des[1]))}\n")
        lose_strk_t=str(max(des[1])) 


        text_file.write('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
        text_file.write(f'TOTAL PNL: {rounded_total_pnl}\n')
        text_file.write(f'TOTAL TRADES: {cummulative_trade}\n')
        text_file.write(f'TOTAL TRADING DAYS: {trading_days}\n')
        text_file.write('\n')   
        text_file.write('DAYWISE\n')
        text_file.write('\n')
        text_file.write(f'PNL PER DAY: {pnl_perday}\n')
        text_file.write(f'Winning Days: {winning_days}\n')
        text_file.write(f'Lossing Days: {lossing_days}\n')
        text_file.write(f'Average Profit On Wining Days: {avg_profit_winning_days}\n')
        text_file.write(f'Average Loss On Lossing Days: {avg_loss_lossing_days}\n')
        text_file.write(f'Max Daily Profit: {max_t}\n')
        text_file.write(f'Max Daily Loss: {min_t}\n')
        text_file.write(f'Winning Streak: {win_strk}\n')
        text_file.write(f'Lossing Streak: {lose_strk}\n')
        text_file.write(f'Day Wise Accuracy: {daywise_accuracy}\n')
        text_file.write('\n')
        text_file.write('TradeWise\n')
        text_file.write('\n')
        text_file.write(f'TOTAL TRADES: {cummulative_trade}\n')
        text_file.write(f'AVERAGE PNL PER TRADE: {pnl_pertrade}\n')
        text_file.write(f'Winning Trades: {winning_trades}\n')
        text_file.write(f'Lossing Trades: {lossing_trades}\n')
        text_file.write(f'Average Profit On Winning Trades: {avg_profit_winning_trades}\n')
        text_file.write(f'Average Loss On Lossing Trades: {avg_loss_lossing_trades}\n')
        text_file.write(f'Max Trade Profit: {max_tt}\n')
        text_file.write(f'Max Trade Loss: {min_tt}\n')
        text_file.write(f'Winning Streak Trade: {win_strk_t}\n')
        text_file.write(f'Lossing Streak Trade: {lose_strk_t}\n')
        text_file.write(f'Trade Wise Accuracy: {tradewise_accuracy}\n')
        text_file.write(f'Target Count: {target_count}\n')
        text_file.write(f'SL Count: {SL_count}\n')
        text_file.write(f'MIS COUNT: {mis_count}\n')


        text_file.write('\n')
        text_file.write(f'DAY WISE PNL(2018) :\n')
        text_file.write('\n')
        text_file.write(f'MONDAY: {rounded_monday_pnl_2018} \n')
        text_file.write(f'TUESDAY: {rounded_tuesday_pnl_2018} \n')
        text_file.write(f'WEDNESDAY: {rounded_wednesday_pnl_2018} \n')
        text_file.write(f'THURSDAY: {rounded_thursday_pnl_2018} \n')
        text_file.write(f'FRIDAY: {rounded_friday_pnl_2018} \n')
        text_file.write('\n')
        text_file.write('MONTH WISE PNL(2018):\n')
        text_file.write('\n')
        text_file.write(f'JANUARY: {rounded_jan_pnl_2018} \n')
        text_file.write(f'FEBRUARY: {rounded_feb_pnl_2018} \n')
        text_file.write(f'MARCH: {rounded_mar_pnl_2018} \n')
        text_file.write(f'APRIL: {rounded_apr_pnl_2018} \n')
        text_file.write(f'MAY: {rounded_may_pnl_2018} \n')
        text_file.write(f'JUNE: {rounded_jun_pnl_2018} \n')
        text_file.write(f'JULY: {rounded_jul_pnl_2018} \n')
        text_file.write(f'AUGUST: {rounded_aug_pnl_2018} \n')
        text_file.write(f'SEPTEMBER: {rounded_sep_pnl_2018} \n')
        text_file.write(f'OCTOBER: {rounded_oct_pnl_2018} \n')
        text_file.write(f'NOVEMBER: {rounded_nov_pnl_2018} \n')
        text_file.write(f'DECEMBER: {rounded_dec_pnl_2018} \n')
        text_file.write('\n')

        text_file.write('\n')
        text_file.write(f'DAY WISE PNL(2019) :\n')
        text_file.write('\n')
        text_file.write(f'MONDAY: {rounded_monday_pnl_2019} \n')
        text_file.write(f'TUESDAY: {rounded_tuesday_pnl_2019} \n')
        text_file.write(f'WEDNESDAY: {rounded_wednesday_pnl_2019} \n')
        text_file.write(f'THURSDAY: {rounded_thursday_pnl_2019} \n')
        text_file.write(f'FRIDAY: {rounded_friday_pnl_2019} \n')
        text_file.write('\n')
        text_file.write('MONTH WISE PNL(2019):\n')
        text_file.write('\n')
        text_file.write(f'JANUARY: {rounded_jan_pnl_2019} \n')
        text_file.write(f'FEBRUARY: {rounded_feb_pnl_2019} \n')
        text_file.write(f'MARCH: {rounded_mar_pnl_2019} \n')
        text_file.write(f'APRIL: {rounded_apr_pnl_2019} \n')
        text_file.write(f'MAY: {rounded_may_pnl_2019} \n')
        text_file.write(f'JUNE: {rounded_jun_pnl_2019} \n')
        text_file.write(f'JULY: {rounded_jul_pnl_2019} \n')
        text_file.write(f'AUGUST: {rounded_aug_pnl_2019} \n')
        text_file.write(f'SEPTEMBER: {rounded_sep_pnl_2019} \n')
        text_file.write(f'OCTOBER: {rounded_oct_pnl_2019} \n')
        text_file.write(f'NOVEMBER: {rounded_nov_pnl_2019} \n')
        text_file.write(f'DECEMBER: {rounded_dec_pnl_2019} \n')
        text_file.write('\n')

        text_file.write('\n')
        text_file.write(f'DAY WISE PNL(2020) :\n')
        text_file.write('\n')
        text_file.write(f'MONDAY: {rounded_monday_pnl_2020} \n')
        text_file.write(f'TUESDAY: {rounded_tuesday_pnl_2020} \n')
        text_file.write(f'WEDNESDAY: {rounded_wednesday_pnl_2020} \n')
        text_file.write(f'THURSDAY: {rounded_thursday_pnl_2020} \n')
        text_file.write(f'FRIDAY: {rounded_friday_pnl_2020} \n')
        text_file.write('\n')
        text_file.write('MONTH WISE PNL(2020):\n')
        text_file.write('\n')
        text_file.write(f'JANUARY: {rounded_jan_pnl_2020} \n')
        text_file.write(f'FEBRUARY: {rounded_feb_pnl_2020} \n')
        text_file.write(f'MARCH: {rounded_mar_pnl_2020} \n')
        text_file.write(f'APRIL: {rounded_apr_pnl_2020} \n')
        text_file.write(f'MAY: {rounded_may_pnl_2020} \n')
        text_file.write(f'JUNE: {rounded_jun_pnl_2020} \n')
        text_file.write(f'JULY: {rounded_jul_pnl_2020} \n')
        text_file.write(f'AUGUST: {rounded_aug_pnl_2020} \n')
        text_file.write(f'SEPTEMBER: {rounded_sep_pnl_2020} \n')
        text_file.write(f'OCTOBER: {rounded_oct_pnl_2020} \n')
        text_file.write(f'NOVEMBER: {rounded_nov_pnl_2020} \n')
        text_file.write(f'DECEMBER: {rounded_dec_pnl_2020} \n')
        text_file.write('\n')
        text_file.write('\n')
        text_file.write(f'DAY WISE PNL(2021) :\n')
        text_file.write('\n')
        text_file.write(f'MONDAY: {rounded_monday_pnl_2021} \n')
        text_file.write(f'TUESDAY: {rounded_tuesday_pnl_2021} \n')
        text_file.write(f'WEDNESDAY: {rounded_wednesday_pnl_2021} \n')
        text_file.write(f'THURSDAY: {rounded_thursday_pnl_2021} \n')
        text_file.write(f'FRIDAY: {rounded_friday_pnl_2021} \n')
        text_file.write('\n')
        text_file.write('MONTH WISE PNL(2021):\n')
        text_file.write('\n')
        text_file.write(f'JANUARY: {rounded_jan_pnl_2021} \n')
        text_file.write(f'FEBRUARY: {rounded_feb_pnl_2021} \n')
        text_file.write(f'MARCH: {rounded_mar_pnl_2021} \n')
        text_file.write(f'APRIL: {rounded_apr_pnl_2021} \n')
        text_file.write(f'MAY: {rounded_may_pnl_2021} \n')
        text_file.write(f'JUNE: {rounded_jun_pnl_2021} \n')
        text_file.write(f'JULY: {rounded_jul_pnl_2021} \n')
        text_file.write(f'AUGUST: {rounded_aug_pnl_2021} \n')
        text_file.write(f'SEPTEMBER: {rounded_sep_pnl_2021} \n')
        text_file.write(f'OCTOBER: {rounded_oct_pnl_2021} \n')
        text_file.write(f'NOVEMBER: {rounded_nov_pnl_2021} \n')
        text_file.write(f'DECEMBER: {rounded_dec_pnl_2021} \n')
        text_file.write('\n')
        text_file.write('\n')
        text_file.write(f'DAY WISE PNL(2022) :\n')
        text_file.write('\n')
        text_file.write(f'MONDAY: {rounded_monday_pnl_2022} \n')
        text_file.write(f'TUESDAY: {rounded_tuesday_pnl_2022} \n')
        text_file.write(f'WEDNESDAY: {rounded_wednesday_pnl_2022} \n')
        text_file.write(f'THURSDAY: {rounded_thursday_pnl_2022} \n')
        text_file.write(f'FRIDAY: {rounded_friday_pnl_2022} \n')
        text_file.write('\n')
        text_file.write('MONTH WISE PNL(2022):\n')
        text_file.write('\n')
        text_file.write(f'JANUARY: {rounded_jan_pnl_2022} \n')
        text_file.write(f'FEBRUARY: {rounded_feb_pnl_2022} \n')
        text_file.write(f'MARCH: {rounded_mar_pnl_2022} \n')
        text_file.write(f'APRIL: {rounded_apr_pnl_2022} \n')
        text_file.write(f'MAY: {rounded_may_pnl_2022} \n')
        text_file.write(f'JUNE: {rounded_jun_pnl_2022} \n')
        text_file.write(f'JULY: {rounded_jul_pnl_2022} \n')
        text_file.write(f'AUGUST: {rounded_aug_pnl_2022} \n')
        text_file.write(f'SEPTEMBER: {rounded_sep_pnl_2022} \n')
        text_file.write(f'OCTOBER: {rounded_oct_pnl_2022} \n')
        text_file.write(f'NOVEMBER: {rounded_nov_pnl_2022} \n')
        text_file.write(f'DECEMBER: {rounded_dec_pnl_2022} \n')


        text_file.write('\n')
        text_file.write(f'DAY WISE PNL(2023) :\n')
        text_file.write('\n')
        text_file.write(f'MONDAY: {rounded_monday_pnl_2023} \n')
        text_file.write(f'TUESDAY: {rounded_tuesday_pnl_2023} \n')
        text_file.write(f'WEDNESDAY: {rounded_wednesday_pnl_2023} \n')
        text_file.write(f'THURSDAY: {rounded_thursday_pnl_2023} \n')
        text_file.write(f'FRIDAY: {rounded_friday_pnl_2023} \n')
        text_file.write('\n')
        text_file.write('MONTH WISE PNL(2023):\n')
        text_file.write('\n')
        text_file.write(f'JANUARY: {rounded_jan_pnl_2023} \n')
        text_file.write(f'FEBRUARY: {rounded_feb_pnl_2023} \n')
        text_file.write(f'MARCH: {rounded_mar_pnl_2023} \n')
        text_file.write(f'APRIL: {rounded_apr_pnl_2023} \n')
        text_file.write(f'MAY: {rounded_may_pnl_2023} \n')
        text_file.write(f'JUNE: {rounded_jun_pnl_2023} \n')
        text_file.write(f'JULY: {rounded_jul_pnl_2023} \n')
        text_file.write(f'AUGUST: {rounded_aug_pnl_2023} \n')
        text_file.write(f'SEPTEMBER: {rounded_sep_pnl_2023} \n')
        text_file.write(f'OCTOBER: {rounded_oct_pnl_2023} \n')
        text_file.write(f'NOVEMBER: {rounded_nov_pnl_2023} \n')
        text_file.write(f'DECEMBER: {rounded_dec_pnl_2023} \n')
        text_file.write('\n')
        text_file.write('\n')


        # text_file.write((max_un_pr), 'Max unrealised Profit during whole Day')
        # text_file.write((max_un_ls), 'Max unrealised Loss during whole Day')


        tpnl.append(total_pnl)
        ttrade.append(cummulative_trade)

        ttdays.append(trading_days) 
        #daywise
        pnlpd.append(pnl_perday)
        wndays.append(winning_days)
        lsdays.append(lossing_days)
        avgpwd.append(avg_profit_winning_days)
        avglld.append(avg_loss_lossing_days)
        mdp.append(f'{max_t}')
        mdl.append(f'{min_t}')
        wnstk.append(win_strk)
        lsstk.append(lose_strk)
        dwacr.append(daywise_accuracy)
        #tradewise
        tttrades.append(cummulative_trade)
        pnlpt.append(pnl_pertrade)
        wntrades.append(winning_trades)
        lstrades.append(lossing_trades)
        avgpwt.append(avg_profit_winning_trades)
        avgllt.append(avg_loss_lossing_trades)
        mtp.append(max_tt)
        mtl.append(min_tt)
        wnstk_t.append(win_strk_t)  
        lsstk_t.append(lose_strk_t)
        twacr.append(tradewise_accuracy)
        slcount.append(SL_count)
        miscount.append(mis_count)
        

        pnl_d = np.array(pnl_d)
        #changehere
        # print(pnl_d, "pnlD")
        if len(pnl_d[pnl_d<0])!=0 and len(pnl_d[pnl_d>0])!=0:

            xs = np.array(pnl_d).cumsum()
            i = np.argmax(np.maximum.accumulate(xs) - xs) # end of the period
            j = np.argmax(xs[:i]) # start of period
            text_file.write('\n')
            day_wise_dd = (xs[i] - xs[j])
            rounded_day_wise_dd = float(format(day_wise_dd, '.2f'))
            text_file.write(f"MAX Drawdown DAY WISE =  {rounded_day_wise_dd}\n")
            fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
            plt.plot(xs)
            plt.plot([i, j], [xs[i], xs[j]], 'o', color='Red', markersize=10)
            x_min, x_max, y_min, y_max = plt.axis()
            plt.xlim(x_min, x_max)
            plt.ylim(y_min, y_max)
            text_x = (x_max + x_min) / 1.8  # Centered horizontally
            text_y = y_max + 0.08 * (y_max - y_min)  # Adjust the factor as needed
            plt.text(text_x, text_y, f'Max DD: {xs[i] - xs[j]:.2f}', fontsize=12, ha='right')
            plt.xlabel('No. of Days')
            plt.ylabel('PNL')
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            # Daywise_chart = f"D:/Backtester/DayWise_BNF_ReEntry_{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.png"
            # if os.path.exists(Daywise_chart):
                # os.remove(Daywise_chart)
            # png_path = 'D:/Backtester.png'
            # plt.savefig(Daywise_chart)
            max_dd=format(float((xs[i] - xs[j])*lot_size))

        else: 
            max_dd = 0
            image_base64 = 0
            day_wise_dd = 0
            margin_req=160000+(float(max_dd)*-1)
            profit_1_lot=(25*total_pnl)
            brokerage=(45*cummulative_trade*2)
            net_pnl=((25*total_pnl)-brokerage)
            roi=(net_pnl/margin_req)*100

        # plt.close()
        tradepnl = np.array(tradepnl)
        #changehere
        # print(tradepnl, "tradepnl")
        # text_file.write(tradepnl[tradepnl>0])
        if len(tradepnl[tradepnl<0])!=0 and len(tradepnl[tradepnl>0])!=0:
            xs = np.array(tradepnl).cumsum()
            i = np.argmax(np.maximum.accumulate(xs) - xs) # end of the period
            j = np.argmax(xs[:i]) # start of period``
            trade_wise_dd = (xs[i] - xs[j])
            rounded_trade_wise_dd = float(format(trade_wise_dd, '.2f'))
            text_file.write(f"MAX Drawdown TRADE WISE =  {rounded_trade_wise_dd}\n")
            # text_file.write(xs[i] - xs[j])
            fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed

            plt.plot(xs)
            plt.plot([i, j], [xs[i], xs[j]], 'o', color='Red', markersize=10)
            # Set the limits of the plot
            x_min, x_max, y_min, y_max = plt.axis()
            plt.xlim(x_min, x_max)
            plt.ylim(y_min, y_max)
            text_x = (x_max + x_min) / 1.8  # Centered horizontally
            text_y = y_max + 0.08 * (y_max - y_min)  # Adjust the factor as needed

            plt.text(text_x, text_y, f'Max DD: {xs[i] - xs[j]:.2f}', fontsize=12, ha='right')
            plt.xlabel('No. of Trades')
            plt.ylabel('PNL')
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            trade_image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            # Tradewise_chart = f"E:/EzQuant/Data/Backtesting_data/Max_DD/TradeWise_BNF_ReEntry_{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.png"
            # if os.path.exists(Tradewise_chart):
            #     os.remove(Tradewise_chart)
            # plt.savefig(Tradewise_chart)

            plt.close()
        else: 
            max_dd = 0
            trade_wise_dd = 0
            trade_image_base64 = 0
            margin_req=160000+(float(max_dd)*-1)
            profit_1_lot=(25*total_pnl)
            brokerage=(45*cummulative_trade*2)
            net_pnl=((25*total_pnl)-brokerage)
            roi=(net_pnl/margin_req)*100


        text_file.write('\n')         

        h=pnl_d
        a=np.array(h)
        no_of_winning_trades=len(a[a >=0])
        daywise_accuracy=float(format((no_of_winning_trades/len(pnl_d))*100,'.2f'))

        g=tradepnl
        g=np.array(g)
        no_of_winning_trades=len(g[g >=0])
        tradewise_accuracy=float(format((no_of_winning_trades/len(tradepnl))*100,'.2f'))

        a=pnl_d
        a=np.array(a)
        winning_trades=(a[a >=0])
        lossing_trades=(a[a <0])
        win_rate = len(winning_trades) / len(a)
        loss_rate = len(lossing_trades) / len(a)


        winning_trades = winning_trades  # List of profits from winning trades
        losing_trades = lossing_trades   # List of losses from losing trades
        if len(winning_trades) == 0 :
            average_gain = 0 
        else:
            average_gain = sum(winning_trades) / len(winning_trades)
        if len(losing_trades) != 0:
            average_loss = sum(losing_trades) / len(losing_trades)
        else:
            average_loss = 0
            # average_loss = 0
        

        expectancy_ratio1 = ((average_gain * win_rate) - (average_loss * loss_rate))/100


        a=tradepnl
        a=np.array(a)
        winning_trades=(a[a >=0])
        lossing_trades=(a[a <0])
        win_rate = len(winning_trades) / len(a)
        loss_rate = len(lossing_trades) / len(a)


        winning_trades = winning_trades  # List of profits from winning trades
        losing_trades = lossing_trades   # List of losses from losing trades
        
        # average_gain = sum(winning_trades) / len(winning_trades)
        # average_loss = sum(losing_trades) / len(losing_trades)

        expectancy_ratio = ((average_gain * win_rate) - (average_loss * loss_rate))/100

        a=pnl_d
        a=np.array(a)

        winning_trades=(a[a >=0])
        lossing_trades=(a[a <0])
        a=tradepnl
        a=np.array(a)

        winning_trades=(a[a >=0])
        lossing_trades=(a[a <0])

        a=list(pnl_d)
        curr_len = 0
        max_len = 0
        curr_len1 = 0
        max_len1 = 0
        for num in a:
            if num > 0:
                curr_len += 1
            else:
                curr_len = 0
            max_len = max(max_len, curr_len)
            if num < 0:
                curr_len1 += 1
            else:
                curr_len1 = 0
            max_len1= max(max_len1, curr_len1)

        monday_roi_2018 = 0
        tuesday_roi_2018 = 0
        wednesday_roi_2018 = 0
        thursday_roi_2018 = 0
        friday_roi_2018 = 0

        monday_roi_2019 = 0
        tuesday_roi_2019 = 0
        wednesday_roi_2019 = 0
        thursday_roi_2019 = 0
        friday_roi_2019 = 0

        monday_roi_2020 = 0
        tuesday_roi_2020 = 0
        wednesday_roi_2020 = 0
        thursday_roi_2020 = 0
        friday_roi_2020 = 0

        monday_roi_2021 = 0
        tuesday_roi_2021 = 0
        wednesday_roi_2021 = 0
        thursday_roi_2021 = 0
        friday_roi_2021 = 0

        monday_roi_2022 = 0
        tuesday_roi_2022 = 0
        wednesday_roi_2022 = 0
        thursday_roi_2022 = 0
        friday_roi_2022 = 0

        monday_roi_2023 = 0
        tuesday_roi_2023 = 0
        wednesday_roi_2023 = 0
        thursday_roi_2023 = 0
        friday_roi_2023 = 0

        rounded_monday_roi_2018 = 0
        rounded_tuesday_roi_2018 = 0
        rounded_wednesday_roi_2018 = 0
        rounded_thursday_roi_2018 = 0
        rounded_friday_roi_2018 = 0

        rounded_monday_roi_2019 = 0
        rounded_tuesday_roi_2019 = 0
        rounded_wednesday_roi_2019 = 0
        rounded_thursday_roi_2019 = 0
        rounded_friday_roi_2019 = 0

        rounded_monday_roi_2020 = 0
        rounded_tuesday_roi_2020 = 0
        rounded_wednesday_roi_2020 = 0
        rounded_thursday_roi_2020 = 0
        rounded_friday_roi_2020 = 0

        rounded_monday_roi_2021 = 0
        rounded_tuesday_roi_2021 = 0
        rounded_wednesday_roi_2021 = 0
        rounded_thursday_roi_2021 = 0
        rounded_friday_roi_2021 = 0
        
        rounded_monday_roi_2022 = 0
        rounded_tuesday_roi_2022 = 0
        rounded_wednesday_roi_2022 = 0
        rounded_thursday_roi_2022 = 0
        rounded_friday_roi_2022 = 0

        rounded_monday_roi_2023 = 0
        rounded_tuesday_roi_2023 = 0
        rounded_wednesday_roi_2023 = 0
        rounded_thursday_roi_2023 = 0
        rounded_friday_roi_2023 = 0

        january_roi_2018 = 0
        february_roi_2018 = 0
        march_roi_2018 = 0
        april_roi_2018 = 0
        may_roi_2018 = 0
        june_roi_2018 = 0
        july_roi_2018 = 0
        august_roi_2018 = 0
        september_roi_2018 = 0
        october_roi_2018 = 0
        november_roi_2018 = 0
        december_roi_2018 = 0

        january_roi_2019 = 0
        february_roi_2019 = 0
        march_roi_2019 = 0
        april_roi_2019 = 0
        may_roi_2019 = 0
        june_roi_2019 = 0
        july_roi_2019 = 0
        august_roi_2019 = 0
        september_roi_2019 = 0
        october_roi_2019 = 0
        november_roi_2019 = 0
        december_roi_2019 = 0

        january_roi_2020 = 0
        february_roi_2020 = 0
        march_roi_2020 = 0
        april_roi_2020 = 0
        may_roi_2020 = 0
        june_roi_2020 = 0
        july_roi_2020 = 0
        august_roi_2020 = 0
        september_roi_2020 = 0
        october_roi_2020 = 0
        november_roi_2020 = 0
        december_roi_2020 = 0

        january_roi_2021 = 0
        february_roi_2021 = 0
        march_roi_2021 = 0
        april_roi_2021 = 0
        may_roi_2021 = 0
        june_roi_2021 = 0
        july_roi_2021 = 0
        august_roi_2021 = 0
        september_roi_2021 = 0
        october_roi_2021 = 0
        november_roi_2021 = 0
        december_roi_2021 = 0

        january_roi_2022 = 0
        february_roi_2022 = 0
        march_roi_2022 = 0
        april_roi_2022 = 0
        may_roi_2022 = 0
        june_roi_2022 = 0
        july_roi_2022 = 0
        august_roi_2022 = 0
        september_roi_2022 = 0
        october_roi_2022 = 0
        november_roi_2022 = 0
        december_roi_2022 = 0

        january_roi_2023 = 0
        february_roi_2023 = 0
        march_roi_2023 = 0
        april_roi_2023 = 0
        may_roi_2023 = 0
        june_roi_2023 = 0
        july_roi_2023 = 0
        august_roi_2023 = 0
        september_roi_2023 = 0
        october_roi_2023 = 0
        november_roi_2023 = 0
        december_roi_2023 = 0

        rounded_january_roi_2018 = 0
        rounded_february_roi_2018 = 0
        rounded_march_roi_2018 = 0
        rounded_april_roi_2018 = 0
        rounded_may_roi_2018 = 0
        rounded_june_roi_2018 = 0
        rounded_july_roi_2018 = 0
        rounded_august_roi_2018 = 0
        rounded_september_roi_2018 = 0
        rounded_october_roi_2018 = 0
        rounded_november_roi_2018 = 0
        rounded_december_roi_2018 = 0

        rounded_january_roi_2019 = 0
        rounded_february_roi_2019 = 0
        rounded_march_roi_2019 = 0
        rounded_april_roi_2019 = 0
        rounded_may_roi_2019 = 0
        rounded_june_roi_2019 = 0
        rounded_july_roi_2019 = 0
        rounded_august_roi_2019 = 0
        rounded_september_roi_2019 = 0
        rounded_october_roi_2019 = 0
        rounded_november_roi_2019 = 0
        rounded_december_roi_2019 = 0

        rounded_january_roi_2020 = 0
        rounded_february_roi_2020 = 0
        rounded_march_roi_2020 = 0
        rounded_april_roi_2020 = 0
        rounded_may_roi_2020 = 0
        rounded_june_roi_2020 = 0
        rounded_july_roi_2020 = 0
        rounded_august_roi_2020 = 0
        rounded_september_roi_2020 = 0
        rounded_october_roi_2020 = 0
        rounded_november_roi_2020 = 0
        rounded_december_roi_2020 = 0

        rounded_january_roi_2021 = 0
        rounded_february_roi_2021 = 0
        rounded_march_roi_2021 = 0
        rounded_april_roi_2021 = 0
        rounded_may_roi_2021 = 0
        rounded_june_roi_2021 = 0
        rounded_july_roi_2021 = 0
        rounded_august_roi_2021 = 0
        rounded_september_roi_2021 = 0
        rounded_october_roi_2021 = 0
        rounded_november_roi_2021 = 0
        rounded_december_roi_2021 = 0

        rounded_january_roi_2022 = 0
        rounded_february_roi_2022 = 0
        rounded_march_roi_2022 = 0
        rounded_april_roi_2022 = 0
        rounded_may_roi_2022 = 0
        rounded_june_roi_2022 = 0
        rounded_july_roi_2022 = 0
        rounded_august_roi_2022 = 0
        rounded_september_roi_2022 = 0
        rounded_october_roi_2022 = 0
        rounded_november_roi_2022 = 0
        rounded_december_roi_2022 = 0

        rounded_january_roi_2023 = 0
        rounded_february_roi_2023 = 0
        rounded_march_roi_2023 = 0
        rounded_april_roi_2023 = 0
        rounded_may_roi_2023 = 0
        rounded_june_roi_2023 = 0
        rounded_july_roi_2023 = 0
        rounded_august_roi_2023 = 0
        rounded_september_roi_2023 = 0
        rounded_october_roi_2023 = 0
        rounded_november_roi_2023 = 0
        rounded_december_roi_2023 = 0
        if max_dd != 0 and (legs[0]['tradetype'] == "BUY" or legs[1]['tradetype'] == "BUY" or (legs[0]['tradetype'] == "BUY" and legs[1]['tradetype'] == "BUY")):
            
            monday_roi_2018 = ((monday_pnl_2018*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2018 = ((tuesday_pnl_2018*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2018 = ((wednesday_pnl_2018*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2018 = ((thursday_pnl_2018*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2018 = ((friday_pnl_2018*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2018 = ((jan_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2018 = ((feb_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2018 = ((mar_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2018 = ((apr_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2018 = ((may_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2018 = ((jun_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2018 = ((jul_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2018 = ((aug_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2018 = ((sep_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2018 = ((oct_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2018 = ((nov_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2018 = ((dec_pnl_2018 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2019 = ((monday_pnl_2019*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2019 = ((tuesday_pnl_2019*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2019 = ((wednesday_pnl_2019*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2019 = ((thursday_pnl_2019*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2019 = ((friday_pnl_2019*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2019 = ((jan_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2019 = ((feb_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2019 = ((mar_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2019 = ((apr_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2019 = ((may_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2019 = ((jun_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2019 = ((jul_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2019 = ((aug_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2019 = ((sep_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2019 = ((oct_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2019 = ((nov_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2019 = ((dec_pnl_2019 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2020 = ((monday_pnl_2020*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2020 = ((tuesday_pnl_2020*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2020 = ((wednesday_pnl_2020*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2020 = ((thursday_pnl_2020*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2020 = ((friday_pnl_2020*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2020 = ((jan_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2020 = ((feb_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2020 = ((mar_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2020 = ((apr_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2020 = ((may_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2020 = ((jun_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2020 = ((jul_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2020 = ((aug_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2020 = ((sep_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2020 = ((oct_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2020 = ((nov_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2020 = ((dec_pnl_2020 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2021 = ((monday_pnl_2021*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2021 = ((tuesday_pnl_2021*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2021 = ((wednesday_pnl_2021*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2021 = ((thursday_pnl_2021*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2021 = ((friday_pnl_2021*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2021 = ((jan_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2021 = ((feb_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2021 = ((mar_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2021 = ((apr_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2021 = ((may_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2021 = ((jun_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2021 = ((jul_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2021 = ((aug_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2021 = ((sep_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2021 = ((oct_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2021 = ((nov_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2021 = ((dec_pnl_2021 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2022 = ((monday_pnl_2022*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2022 = ((tuesday_pnl_2022*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2022 = ((wednesday_pnl_2022*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2022 = ((thursday_pnl_2022*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2022 = ((friday_pnl_2022*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2022 = ((jan_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2022 = ((feb_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2022 = ((mar_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2022 = ((apr_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2022 = ((may_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2022 = ((jun_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2022 = ((jul_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2022 = ((aug_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2022 = ((sep_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2022 = ((oct_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2022 = ((nov_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2022 = ((dec_pnl_2022 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2023 = ((monday_pnl_2023*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2023 = ((tuesday_pnl_2023*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2023 = ((wednesday_pnl_2023*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2023 = ((thursday_pnl_2023*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2023 = ((friday_pnl_2023*lot_size)/(10000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2023 = ((jan_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2023 = ((feb_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2023 = ((mar_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2023 = ((apr_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2023 = ((may_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2023 = ((jun_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2023 = ((jul_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2023 = ((aug_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2023 = ((sep_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2023 = ((oct_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2023 = ((nov_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2023 = ((dec_pnl_2023 *lot_size) / (10000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
        elif max_dd != 0 and (legs[0]['tradetype'] == "SELL" or legs[1]['tradetype'] == "SELL" or (legs[0]['tradetype'] == "SELL" and legs[1]['tradetype'] == "SELL")):
            monday_roi_2018 = ((monday_pnl_2018*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2018 = ((tuesday_pnl_2018*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2018 = ((wednesday_pnl_2018*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2018 = ((thursday_pnl_2018*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2018 = ((friday_pnl_2018*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2018 = ((jan_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2018 = ((feb_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2018 = ((mar_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2018 = ((apr_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2018 = ((may_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2018 = ((jun_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2018 = ((jul_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2018 = ((aug_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2018 = ((sep_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2018 = ((oct_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2018 = ((nov_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2018 = ((dec_pnl_2018 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2019 = ((monday_pnl_2019*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2019 = ((tuesday_pnl_2019*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2019 = ((wednesday_pnl_2019*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2019 = ((thursday_pnl_2019*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2019 = ((friday_pnl_2019*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2019 = ((jan_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2019 = ((feb_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2019 = ((mar_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2019 = ((apr_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2019 = ((may_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2019 = ((jun_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2019 = ((jul_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2019 = ((aug_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2019 = ((sep_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2019 = ((oct_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2019 = ((nov_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2019 = ((dec_pnl_2019 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2020 = ((monday_pnl_2020*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2020 = ((tuesday_pnl_2020*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2020 = ((wednesday_pnl_2020*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2020 = ((thursday_pnl_2020*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2020 = ((friday_pnl_2020*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2020 = ((jan_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2020 = ((feb_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2020 = ((mar_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2020 = ((apr_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2020 = ((may_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2020 = ((jun_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2020 = ((jul_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2020 = ((aug_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2020 = ((sep_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2020 = ((oct_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2020 = ((nov_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2020 = ((dec_pnl_2020 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2021 = ((monday_pnl_2021*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2021 = ((tuesday_pnl_2021*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2021 = ((wednesday_pnl_2021*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2021 = ((thursday_pnl_2021*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2021 = ((friday_pnl_2021*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2021 = ((jan_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2021 = ((feb_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2021 = ((mar_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2021 = ((apr_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2021 = ((may_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2021 = ((jun_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2021 = ((jul_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2021 = ((aug_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2021 = ((sep_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2021 = ((oct_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2021 = ((nov_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2021 = ((dec_pnl_2021 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2022 = ((monday_pnl_2022*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2022 = ((tuesday_pnl_2022*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2022 = ((wednesday_pnl_2022*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2022 = ((thursday_pnl_2022*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2022 = ((friday_pnl_2022*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2022 = ((jan_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2022 = ((feb_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2022 = ((mar_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2022 = ((apr_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2022 = ((may_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2022 = ((jun_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2022 = ((jul_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2022 = ((aug_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2022 = ((sep_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2022 = ((oct_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2022 = ((nov_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2022 = ((dec_pnl_2022 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            monday_roi_2023 = ((monday_pnl_2023*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            tuesday_roi_2023 = ((tuesday_pnl_2023*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            wednesday_roi_2023 = ((wednesday_pnl_2023*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            thursday_roi_2023 = ((thursday_pnl_2023*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            friday_roi_2023 = ((friday_pnl_2023*lot_size)/(160000+((max(day_wise_dd, trade_wise_dd))*lot_size)))*100
            january_roi_2023 = ((jan_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            february_roi_2023 = ((feb_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            march_roi_2023 = ((mar_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            april_roi_2023 = ((apr_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            may_roi_2023 = ((may_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            june_roi_2023 = ((jun_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            july_roi_2023 = ((jul_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            august_roi_2023 = ((aug_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            september_roi_2023 = ((sep_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            october_roi_2023 = ((oct_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            november_roi_2023 = ((nov_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
            december_roi_2023 = ((dec_pnl_2023 *lot_size) / (160000 + ((max(day_wise_dd, trade_wise_dd)) *lot_size))) * 100
        
        rounded_monday_2022 = float(format(monday_pnl_2022, '.2f'))
        rounded_tuesday_2022 = float(format(tuesday_pnl_2022, '.2f'))
        rounded_wednesday_2022 = float(format(wednesday_pnl_2022, '.2f'))
        rounded_thursday_2022 = float(format(thursday_pnl_2022, '.2f'))
        rounded_friday_2022 = float(format(friday_pnl_2022, '.2f'))

        rounded_monday_roi_2022 = float(format(monday_roi_2022, '.2f'))
        rounded_tuesday_roi_2022 = float(format(tuesday_roi_2022, '.2f'))
        rounded_wednesday_roi_2022 = float(format(wednesday_roi_2022, '.2f'))
        rounded_thursday_roi_2022 = float(format(thursday_roi_2022, '.2f'))
        rounded_friday_roi_2022 = float(format(friday_roi_2022, '.2f'))

        rounded_january_2022 = float(format(jan_pnl_2022, '.2f'))
        rounded_february_2022 = float(format(feb_pnl_2022, '.2f'))
        rounded_march_2022 = float(format(mar_pnl_2022, '.2f'))
        rounded_april_2022 = float(format(apr_pnl_2022, '.2f'))
        rounded_may_2022 = float(format(may_pnl_2022, '.2f'))
        rounded_june_2022 = float(format(jun_pnl_2022, '.2f'))
        rounded_july_2022 = float(format(jul_pnl_2022, '.2f'))
        rounded_august_2022 = float(format(aug_pnl_2022, '.2f'))
        rounded_september_2022 = float(format(sep_pnl_2022, '.2f'))
        rounded_october_2022 = float(format(oct_pnl_2022, '.2f'))
        rounded_november_2022 = float(format(nov_pnl_2022, '.2f'))
        rounded_december_2022= float(format(dec_pnl_2022, '.2f'))

        rounded_january_roi_2022 = float(format(january_roi_2022, '.2f'))
        rounded_february_roi_2022 = float(format(february_roi_2022, '.2f'))
        rounded_march_roi_2022 = float(format(march_roi_2022, '.2f'))
        rounded_april_roi_2022 = float(format(april_roi_2022, '.2f'))
        rounded_may_roi_2022 = float(format(may_roi_2022, '.2f'))
        rounded_june_roi_2022 = float(format(june_roi_2022, '.2f'))
        rounded_july_roi_2022 = float(format(july_roi_2022, '.2f'))
        rounded_august_roi_2022 = float(format(august_roi_2022, '.2f'))
        rounded_september_roi_2022 = float(format(september_roi_2022, '.2f'))
        rounded_october_roi_2022 = float(format(october_roi_2022, '.2f'))
        rounded_november_roi_2022 = float(format(november_roi_2022, '.2f'))
        rounded_december_roi_2022 = float(format(december_roi_2022, '.2f'))

        rounded_max_un_pr = np.round(max_un_pr, 2)
        rounded_max_un_ls = np.round(max_un_ls, 2)

        total_pnl_2022 = rounded_january_2022 + rounded_february_2022 + rounded_march_2022 + rounded_april_2022 + \
                    rounded_may_2022 + rounded_june_2022 + rounded_july_2022 + rounded_august_2022 + \
                    rounded_september_2022 + rounded_october_2022 + rounded_november_2022 + rounded_december_2022



        rounded_monday_2023 = float(format(monday_pnl_2023, '.2f'))
        rounded_tuesday_2023 = float(format(tuesday_pnl_2023, '.2f'))
        rounded_wednesday_2023 = float(format(wednesday_pnl_2023, '.2f'))
        rounded_thursday_2023 = float(format(thursday_pnl_2023, '.2f'))
        rounded_friday_2023 = float(format(friday_pnl_2023, '.2f'))

        rounded_monday_roi_2023 = float(format(monday_roi_2023, '.2f'))
        rounded_tuesday_roi_2023 = float(format(tuesday_roi_2023, '.2f'))
        rounded_wednesday_roi_2023 = float(format(wednesday_roi_2023, '.2f'))
        rounded_thursday_roi_2023 = float(format(thursday_roi_2023, '.2f'))
        rounded_friday_roi_2023 = float(format(friday_roi_2023, '.2f'))

        rounded_january_2023 = float(format(jan_pnl_2023, '.2f'))
        rounded_february_2023 = float(format(feb_pnl_2023, '.2f'))
        rounded_march_2023 = float(format(mar_pnl_2023, '.2f'))
        rounded_april_2023 = float(format(apr_pnl_2023, '.2f'))
        rounded_may_2023 = float(format(may_pnl_2023, '.2f'))
        rounded_june_2023 = float(format(jun_pnl_2023, '.2f'))
        rounded_july_2023 = float(format(jul_pnl_2023, '.2f'))
        rounded_august_2023 = float(format(aug_pnl_2023, '.2f'))
        rounded_september_2023 = float(format(sep_pnl_2023, '.2f'))
        rounded_october_2023 = float(format(oct_pnl_2023, '.2f'))
        rounded_november_2023 = float(format(nov_pnl_2023, '.2f'))
        rounded_december_2023= float(format(dec_pnl_2023, '.2f'))


        rounded_january_roi_2023 = float(format(january_roi_2023, '.2f'))
        rounded_february_roi_2023 = float(format(february_roi_2023, '.2f'))
        rounded_march_roi_2023 = float(format(march_roi_2023, '.2f'))
        rounded_april_roi_2023 = float(format(april_roi_2023, '.2f'))
        rounded_may_roi_2023 = float(format(may_roi_2023, '.2f'))
        rounded_june_roi_2023 = float(format(june_roi_2023, '.2f'))
        rounded_july_roi_2023 = float(format(july_roi_2023, '.2f'))
        rounded_august_roi_2023 = float(format(august_roi_2023, '.2f'))
        rounded_september_roi_2023 = float(format(september_roi_2023, '.2f'))
        rounded_october_roi_2023 = float(format(october_roi_2023, '.2f'))
        rounded_november_roi_2023 = float(format(november_roi_2023, '.2f'))
        rounded_december_roi_2023 = float(format(december_roi_2023, '.2f'))


        rounded_max_un_pr = np.round(max_un_pr, 2)
        rounded_max_un_ls = np.round(max_un_ls, 2)

        total_pnl_2023 = rounded_january_2023 + rounded_february_2023 + rounded_march_2023 + rounded_april_2023 + \
                    rounded_may_2023 + rounded_june_2023 + rounded_july_2023 + rounded_august_2023 + \
                    rounded_september_2023 + rounded_october_2023 + rounded_november_2023 + rounded_december_2023



        rounded_monday_2021 = float(format(monday_pnl_2021, '.2f'))
        rounded_tuesday_2021 = float(format(tuesday_pnl_2021, '.2f'))
        rounded_wednesday_2021 = float(format(wednesday_pnl_2021, '.2f'))
        rounded_thursday_2021 = float(format(thursday_pnl_2021, '.2f'))
        rounded_friday_2021 = float(format(friday_pnl_2021, '.2f'))
        
        rounded_monday_roi_2021 = float(format(monday_roi_2021, '.2f'))
        rounded_tuesday_roi_2021 = float(format(tuesday_roi_2021, '.2f'))
        rounded_wednesday_roi_2021 = float(format(wednesday_roi_2021, '.2f'))
        rounded_thursday_roi_2021 = float(format(thursday_roi_2021, '.2f'))
        rounded_friday_roi_2021 = float(format(friday_roi_2021, '.2f'))
        
        rounded_january_2021 = float(format(jan_pnl_2021, '.2f'))
        rounded_february_2021 = float(format(feb_pnl_2021, '.2f'))
        rounded_march_2021 = float(format(mar_pnl_2021, '.2f'))
        rounded_april_2021 = float(format(apr_pnl_2021, '.2f'))
        rounded_may_2021 = float(format(may_pnl_2021, '.2f'))
        rounded_june_2021 = float(format(jun_pnl_2021, '.2f'))
        rounded_july_2021 = float(format(jul_pnl_2021, '.2f'))
        rounded_august_2021 = float(format(aug_pnl_2021, '.2f'))
        rounded_september_2021 = float(format(sep_pnl_2021, '.2f'))
        rounded_october_2021 = float(format(oct_pnl_2021, '.2f'))
        rounded_november_2021 = float(format(nov_pnl_2021, '.2f'))
        rounded_december_2021= float(format(dec_pnl_2021, '.2f'))


        rounded_january_roi_2021 = float(format(january_roi_2021, '.2f'))
        rounded_february_roi_2021 = float(format(february_roi_2021, '.2f'))
        rounded_march_roi_2021 = float(format(march_roi_2021, '.2f'))
        rounded_april_roi_2021 = float(format(april_roi_2021, '.2f'))
        rounded_may_roi_2021 = float(format(may_roi_2021, '.2f'))
        rounded_june_roi_2021 = float(format(june_roi_2021, '.2f'))
        rounded_july_roi_2021 = float(format(july_roi_2021, '.2f'))
        rounded_august_roi_2021 = float(format(august_roi_2021, '.2f'))
        rounded_september_roi_2021 = float(format(september_roi_2021, '.2f'))
        rounded_october_roi_2021 = float(format(october_roi_2021, '.2f'))
        rounded_november_roi_2021 = float(format(november_roi_2021, '.2f'))
        rounded_december_roi_2021 = float(format(december_roi_2021, '.2f'))

        total_pnl_2021 = rounded_january_2021 + rounded_february_2021 + rounded_march_2021 + rounded_april_2021 + \
                    rounded_may_2021 + rounded_june_2021 + rounded_july_2021 + rounded_august_2021 + \
                    rounded_september_2021 + rounded_october_2021 + rounded_november_2021 + rounded_december_2021

        rounded_monday_2020 = float(format(monday_pnl_2020, '.2f'))
        rounded_tuesday_2020 = float(format(tuesday_pnl_2020, '.2f'))
        rounded_wednesday_2020 = float(format(wednesday_pnl_2020, '.2f'))
        rounded_thursday_2020 = float(format(thursday_pnl_2020, '.2f'))
        rounded_friday_2020 = float(format(friday_pnl_2020, '.2f'))
        
        rounded_monday_roi_2020 = float(format(monday_roi_2020, '.2f'))
        rounded_tuesday_roi_2020 = float(format(tuesday_roi_2020, '.2f'))
        rounded_wednesday_roi_2020 = float(format(wednesday_roi_2020, '.2f'))
        rounded_thursday_roi_2020 = float(format(thursday_roi_2020, '.2f'))
        rounded_friday_roi_2020 = float(format(friday_roi_2020, '.2f'))
        
        rounded_january_2020 = float(format(jan_pnl_2020, '.2f'))
        rounded_february_2020 = float(format(feb_pnl_2020, '.2f'))
        rounded_march_2020 = float(format(mar_pnl_2020, '.2f'))
        rounded_april_2020 = float(format(apr_pnl_2020, '.2f'))
        rounded_may_2020 = float(format(may_pnl_2020, '.2f'))
        rounded_june_2020 = float(format(jun_pnl_2020, '.2f'))
        rounded_july_2020 = float(format(jul_pnl_2020, '.2f'))
        rounded_august_2020 = float(format(aug_pnl_2020, '.2f'))
        rounded_september_2020 = float(format(sep_pnl_2020, '.2f'))
        rounded_october_2020 = float(format(oct_pnl_2020, '.2f'))
        rounded_november_2020 = float(format(nov_pnl_2020, '.2f'))
        rounded_december_2020= float(format(dec_pnl_2020, '.2f'))

        rounded_january_roi_2020 = float(format(january_roi_2020, '.2f'))
        rounded_february_roi_2020 = float(format(february_roi_2020, '.2f'))
        rounded_march_roi_2020 = float(format(march_roi_2020, '.2f'))
        rounded_april_roi_2020 = float(format(april_roi_2020, '.2f'))
        rounded_may_roi_2020 = float(format(may_roi_2020, '.2f'))
        rounded_june_roi_2020 = float(format(june_roi_2020, '.2f'))
        rounded_july_roi_2020 = float(format(july_roi_2020, '.2f'))
        rounded_august_roi_2020 = float(format(august_roi_2020, '.2f'))
        rounded_september_roi_2020 = float(format(september_roi_2020, '.2f'))
        rounded_october_roi_2020 = float(format(october_roi_2020, '.2f'))
        rounded_november_roi_2020 = float(format(november_roi_2020, '.2f'))
        rounded_december_roi_2020 = float(format(december_roi_2020, '.2f'))

        total_pnl_2020 = rounded_january_2020 + rounded_february_2020 + rounded_march_2020 + rounded_april_2020 + \
                    rounded_may_2020 + rounded_june_2020 + rounded_july_2020 + rounded_august_2020 + \
                    rounded_september_2020 + rounded_october_2020 + rounded_november_2020 + rounded_december_2020

        rounded_monday_2019 = float(format(monday_pnl_2019, '.2f'))
        rounded_tuesday_2019 = float(format(tuesday_pnl_2019, '.2f'))
        rounded_wednesday_2019 = float(format(wednesday_pnl_2019, '.2f'))
        rounded_thursday_2019 = float(format(thursday_pnl_2019, '.2f'))
        rounded_friday_2019 = float(format(friday_pnl_2019, '.2f'))
        
        rounded_monday_roi_2019 = float(format(monday_roi_2019, '.2f'))
        rounded_tuesday_roi_2019 = float(format(tuesday_roi_2019, '.2f'))
        rounded_wednesday_roi_2019 = float(format(wednesday_roi_2019, '.2f'))
        rounded_thursday_roi_2019 = float(format(thursday_roi_2019, '.2f'))
        rounded_friday_roi_2019 = float(format(friday_roi_2019, '.2f'))
        
        rounded_january_2019 = float(format(jan_pnl_2019, '.2f'))
        rounded_february_2019 = float(format(feb_pnl_2019, '.2f'))
        rounded_march_2019 = float(format(mar_pnl_2019, '.2f'))
        rounded_april_2019 = float(format(apr_pnl_2019, '.2f'))
        rounded_may_2019 = float(format(may_pnl_2019, '.2f'))
        rounded_june_2019 = float(format(jun_pnl_2019, '.2f'))
        rounded_july_2019 = float(format(jul_pnl_2019, '.2f'))
        rounded_august_2019 = float(format(aug_pnl_2019, '.2f'))
        rounded_september_2019 = float(format(sep_pnl_2019, '.2f'))
        rounded_october_2019 = float(format(oct_pnl_2019, '.2f'))
        rounded_november_2019 = float(format(nov_pnl_2019, '.2f'))
        rounded_december_2019= float(format(dec_pnl_2019, '.2f'))


        rounded_january_roi_2019 = float(format(january_roi_2019, '.2f'))
        rounded_february_roi_2019 = float(format(february_roi_2019, '.2f'))
        rounded_march_roi_2019 = float(format(march_roi_2019, '.2f'))
        rounded_april_roi_2019 = float(format(april_roi_2019, '.2f'))
        rounded_may_roi_2019 = float(format(may_roi_2019, '.2f'))
        rounded_june_roi_2019 = float(format(june_roi_2019, '.2f'))
        rounded_july_roi_2019 = float(format(july_roi_2019, '.2f'))
        rounded_august_roi_2019 = float(format(august_roi_2019, '.2f'))
        rounded_september_roi_2019 = float(format(september_roi_2019, '.2f'))
        rounded_october_roi_2019 = float(format(october_roi_2019, '.2f'))
        rounded_november_roi_2019 = float(format(november_roi_2019, '.2f'))
        rounded_december_roi_2019 = float(format(december_roi_2019, '.2f'))

        total_pnl_2019 = rounded_january_2019 + rounded_february_2019 + rounded_march_2019 + rounded_april_2019 + \
                    rounded_may_2019 + rounded_june_2019 + rounded_july_2019 + rounded_august_2019 + \
                    rounded_september_2019 + rounded_october_2019 + rounded_november_2019 + rounded_december_2019

        rounded_monday_2018 = float(format(monday_pnl_2018, '.2f'))
        rounded_tuesday_2018 = float(format(tuesday_pnl_2018, '.2f'))
        rounded_wednesday_2018 = float(format(wednesday_pnl_2018, '.2f'))
        rounded_thursday_2018 = float(format(thursday_pnl_2018, '.2f'))
        rounded_friday_2018 = float(format(friday_pnl_2018, '.2f'))
        
        rounded_monday_roi_2018 = float(format(monday_roi_2018, '.2f'))
        rounded_tuesday_roi_2018 = float(format(tuesday_roi_2018, '.2f'))
        rounded_wednesday_roi_2018 = float(format(wednesday_roi_2018, '.2f'))
        rounded_thursday_roi_2018 = float(format(thursday_roi_2018, '.2f'))
        rounded_friday_roi_2018 = float(format(friday_roi_2018, '.2f'))
        
        rounded_january_2018 = float(format(jan_pnl_2018, '.2f'))
        rounded_february_2018 = float(format(feb_pnl_2018, '.2f'))
        rounded_march_2018 = float(format(mar_pnl_2018, '.2f'))
        rounded_april_2018 = float(format(apr_pnl_2018, '.2f'))
        rounded_may_2018 = float(format(may_pnl_2018, '.2f'))
        rounded_june_2018 = float(format(jun_pnl_2018, '.2f'))
        rounded_july_2018 = float(format(jul_pnl_2018, '.2f'))
        rounded_august_2018 = float(format(aug_pnl_2018, '.2f'))
        rounded_september_2018 = float(format(sep_pnl_2018, '.2f'))
        rounded_october_2018 = float(format(oct_pnl_2018, '.2f'))
        rounded_november_2018 = float(format(nov_pnl_2018, '.2f'))
        rounded_december_2018= float(format(dec_pnl_2018, '.2f'))


        rounded_january_roi_2018 = float(format(january_roi_2018, '.2f'))
        rounded_february_roi_2018 = float(format(february_roi_2018, '.2f'))
        rounded_march_roi_2018 = float(format(march_roi_2018, '.2f'))
        rounded_april_roi_2018 = float(format(april_roi_2018, '.2f'))
        rounded_may_roi_2018 = float(format(may_roi_2018, '.2f'))
        rounded_june_roi_2018 = float(format(june_roi_2018, '.2f'))
        rounded_july_roi_2018 = float(format(july_roi_2018, '.2f'))
        rounded_august_roi_2018 = float(format(august_roi_2018, '.2f'))
        rounded_september_roi_2018 = float(format(september_roi_2018, '.2f'))
        rounded_october_roi_2018 = float(format(october_roi_2018, '.2f'))
        rounded_november_roi_2018 = float(format(november_roi_2018, '.2f'))
        rounded_december_roi_2018 = float(format(december_roi_2018, '.2f'))

        total_pnl_2018 = rounded_january_2018 + rounded_february_2018 + rounded_march_2018 + rounded_april_2018 + \
                    rounded_may_2018 + rounded_june_2018 + rounded_july_2018 + rounded_august_2018 + \
                    rounded_september_2018 + rounded_october_2018 + rounded_november_2018 + rounded_december_2018
        
        rounded_pnl_d = np.round(pnl_d, 2)
        rounded_cumulative_pnl = np.round(cumulative_pnl, 2)

        rounded_tradepnl = np.round(tradepnl, 2)
        rounded_max_run_up_profit = np.round(max_run_up_profit, 2)

        rounded_max_run_up_loss = np.round(max_run_up_loss, 2)
        rounded_max_un_pr = np.round(max_un_pr, 2)
        rounded_max_un_ls = np.round(max_un_ls, 2)

    #changehere
    # print("-----------------------------------`")
    # print(len(datee), 'Date')
    # print(len(pnl_d), 'PNL')
    # print(len(expiry_day), 'Expiry')
    # print(len(trades), 'No of Trades')
    # print(len(per_change_max_column), 'Spot % Change High')
    # print(len(per_change_min_column), 'Spot % Change Low')
    # print(len(per_change_close_column), 'Spot % Change Close')
    # print(len(cumulative_pnl), 'Cumulative PNL')
    # print(len(max_un_pr), 'Max unrealised Profit during whole Day')
    # print(len(max_un_ls), 'Max unrealised Loss during whole Day')

    # print("-----------------------------------`")
    # print((datee), 'Date')
    # print((pnl_d), 'PNL')
    # print((expiry_day), 'Expiry')
    # print((trades), 'No of Trades')
    # print((per_change_max_column), 'Spot % Change High')
    # print(per_change_min_column, 'Spot % Change Low')
    # print(per_change_close_column, 'Spot % Change Close')
    # print((cumulative_pnl), 'Cumulative PNL')




    # 'Spot % Change Close':per_change_close_column, 'Cumulative PNL': cumulative_pnl, 'Max unrealised Profit during whole Day': max_un_pr, 'Max unrealised Loss during whole Day': max_un_ls}

    ###################################################### Daywise Logs #######################################################

    dictt={'Date':datee,'PNL':rounded_pnl_d,'Expiry':expiry_day,'Number of Trades':trades, 'Spot % Change High':per_change_max_column, 'Spot % Change Low':per_change_min_column, 'Spot % Change Close':per_change_close_column, 'Cumulative PNL': rounded_cumulative_pnl, 'Max unrealised Profit during whole Day': rounded_max_un_pr, 'Max unrealised Loss during whole Day': rounded_max_un_ls}
    dff1=pd.DataFrame(dictt)

    ###################################################### Daywise Logs #######################################################


    # text_file.write(max_run_up_loss)
    # text_file.write(max_run_up_profit)
    # text_file.write(len(trade_day))
    # text_file.write(len(trade_dt))
    # text_file.write(len(trade_exp))
    # text_file.write((trade_typel))
    # text_file.write(len(instrument))
    # text_file.write(len(entry_t))
    # text_file.write(len(tradepnl))


    # text_file.write("-----------------------------------`")
    # text_file.write(len(trade_day), 'day')
    # text_file.write(len(trade_dt), 'date')
    # text_file.write(len(trade_exp), 'Expiry')
    # text_file.write(len(trade_typel), 'tradetype')
    # text_file.write(len(instrument), 'instrument')
    # text_file.write(len(entry_t), 'entrytime')
    # text_file.write(len(entry_p), 'entrypremium')
    # text_file.write(len(exit_t), 'exittime')
    # text_file.write(len(exit_p), 'exit_premium')
    # text_file.write(len(tradepnl), 'PNL')
    # text_file.write(len(max_run_up_profit), 'Max unrealised Profit during whole trade')
    # text_file.write(len(max_run_up_loss), 'Max unrealised loss during whole trade')
    # text_file.write("-----------------------------------`")
    # text_file.write("-----------------------------------`")
    # text_file.write((trade_day), 'day')
    # text_file.write((trade_dt), 'date')
    # text_file.write((trade_exp), 'Expiry')
    # text_file.write((trade_typel), 'tradetype')
    # text_file.write((instrument), 'instrument')
    # text_file.write((entry_t), 'entrytime')
    # text_file.write((entry_p), 'entrypremium')
    # text_file.write((exit_t), 'exittime')
    # text_file.write((exit_p), 'exit_premium')
    # text_file.write((tradepnl), 'PNL')
    # text_file.write((max_run_up_profit), 'Max unrealised Profit during whole trade')
    # text_file.write((max_run_up_loss), 'Max unrealised loss during whole trade')

    dff2=pd.DataFrame(temp_99)
    ####################################################### Tradewise Logs #######################################################
    # dict4={'day':trade_day,'date':trade_dt,'expiry':trade_exp,'tradetype':trade_typel,'instrument':instrument,'entrytime':entry_t,'entrypremium':entry_p,'exittime':exit_t,'exitpremium':exit_p,'PNL':tradepnl,' Max unrealised Profit during whole trade':max_run_up_profit, ' Max unrealised loss during whole trade':max_run_up_loss, "Number of Trades": "None"}
    # dff2=pd.DataFrame(dict4)
    dict4={'Instrument':instrument,'entrytime':entry_t,'entry_premium':entry_p}
    dff3=pd.DataFrame(dict4)
    # dff3.to_csv("dfdfdf.csv")
    dff2['Entry Time']=None
    for j in range(len(dff3)):
        for k in range(len(dff2)):
            if dff2['Instrument'][k] == dff3['Instrument'][j] and dff2['Entry Premium'][k] == dff3['entry_premium'][j]:
                dff2.loc[k, 'Entry Time'] = dff3['entrytime'][j]
    ###################################################### Tradewise Logs #######################################################
    # dff2=df123

    dff2['# Trades'] = range(1, len(dff2) + 1)
    dff1['Index'] = range(1, len(dff1) + 1)

    # Insert '# Trades' column as the first column
    dff1.insert(0, 'Index', dff1.pop('Index'))
    dff2.insert(0, '#Trades', dff2.pop('# Trades'))
    dff2.insert(6, 'Entry Time', dff2.pop('Entry Time'))
    # dff2 = dff2.set_index("#Trades")
    # print(dff2)
    # dff1.to_csv(f'daywise.csv')
    # dff2.to_csv(f'tradewise.csv')


    entrytime_str0 = str(legs[0]['entrytime'])
    entrytime0 = entrytime_str0.replace(':', '_')
    entrytime_str1 = str(legs[0]['entrytime'])
    entrytime1 = entrytime_str1.replace(':', '_')

    exittime_str0 = str(legs[0]['exittime'])
    exittime0 = exittime_str0.replace(':', '_')
    exittime_str1 = str(legs[0]['exittime'])
    exittime1 = exittime_str1.replace(':', '_')
    # #PATH
    # dff1.to_csv(f"backtest/CSV/Daywise_Only_Expiry_BNF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{entrytime0}_{entrytime1}_ExitTime_{exittime0}_{entrytime1}.csv")
    #PATH
    # dff1.to_csv(f"E:/EzQuant/Data/Backtesting_data/CSV/BNF/Daywise_Only_Expiry_BNF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.csv")
    # dff2.to_csv(f"backtest/CSV/Tradewise_Only_Expiry_BNF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{entrytime0}_{entrytime1}_ExitTime_{exittime0}_{entrytime1}.csv")


    data_length = len(dff1)
    data_length2 = len(dff2)


    expectancy_ratio1 = ((average_gain * win_rate) - (average_loss * loss_rate))/100
    day_wise_dd = "{:.2f}".format(day_wise_dd)
    day_wise_dd = float(day_wise_dd)
    if legs[0]['trading_instrument'] == 1:
        day_wise_dd_rupees = day_wise_dd * lot_size
    else:
        day_wise_dd_rupees = day_wise_dd * lot_size
    day_wise_dd_rupees = round(day_wise_dd_rupees, 2)
    expectancy_ratio = ((average_gain * win_rate) - (average_loss * loss_rate))/100


    net_profit = "{:.2f}".format(sum(pnl_d))
    net_profit_points = "{:.2f}".format(sum(tradepnl *lot_size))
    trading_days = len(pnl_d)
    avg_profit_per_day = "{:.2f}".format(np.average(pnl_d))
    avg_profit_per_day = float(avg_profit_per_day)
    avg_profit_per_day = round(avg_profit_per_day, 2)

    if legs[0]['trading_instrument'] == 1:
        avg_profit_per_day_rupees = avg_profit_per_day * lot_size
    else:
        avg_profit_per_day_rupees = avg_profit_per_day * lot_size
    avg_profit_per_day_rupees = round(avg_profit_per_day_rupees, 2)
    if legs[0]['trading_instrument'] == 1:
        max_tt_rupees = max_tt * lot_size    
    else:
        max_tt_rupees = max_tt * lot_size
    max_tt_rupees = round(max_tt_rupees, 2)
    if legs[0]['trading_instrument'] == 1:
        min_tt_rupees = min_tt * lot_size    
    else:
        min_tt_rupees = min_tt * lot_size
    min_tt_rupees = round(min_tt_rupees, 2)

    if legs[0]['trading_instrument'] == 1:
        avg_profit_winning_days_rupees = avg_profit_winning_days * lot_size    
    else:
        avg_profit_winning_days_rupees = avg_profit_winning_days * lot_size
    if legs[0]['trading_instrument'] == 1:
        avg_profit_winning_trades_rupees = avg_profit_winning_trades * lot_size    
    else:
        avg_profit_winning_trades_rupees = avg_profit_winning_trades * lot_size
    if legs[0]['trading_instrument'] == 1:
        avg_loss_lossing_days_rupees = avg_loss_lossing_days * lot_size    
    else:
        avg_loss_lossing_days_rupees = avg_loss_lossing_days * lot_size
    if legs[0]['trading_instrument'] == 1:
        avg_loss_lossing_trades_rupees = avg_loss_lossing_trades * lot_size    
    else:
        avg_loss_lossing_trades_rupees = avg_loss_lossing_trades * lot_size
    avg_loss_lossing_trades_rupees = round(avg_loss_lossing_trades_rupees, 2)
    avg_loss_lossing_days_rupees = round(avg_loss_lossing_days_rupees, 2)
    avg_profit_winning_days_rupees = round(avg_profit_winning_days_rupees, 2)
    avg_profit_winning_trades_rupees = round(avg_profit_winning_trades_rupees, 2)

    rounded_avg_profit_per_day = "{:.2f}".format(np.average(pnl_d))

    winning_days = len(pnl_d[pnl_d >= 0])
    losing_days = len(pnl_d[pnl_d < 0])
    daywise_accuracy = "{:.2f}".format((winning_days / len(pnl_d)) * 100)

    num_trades = len(tradepnl)
    avg_profit_per_trade = "{:.2f}".format(np.average(tradepnl))
    avg_profit_per_trade = float(avg_profit_per_trade)
    if legs[0]['trading_instrument'] == 1:
        avg_profit_per_trade_rupees = avg_profit_per_trade * lot_size    
    else:
        avg_profit_per_trade_rupees = avg_profit_per_trade * lot_size
    avg_profit_per_trade_rupees = round(avg_profit_per_trade_rupees, 2)

    if legs[0]['trading_instrument'] == 1:
        max_t_rupees = max_t * lot_size    
    else:
        max_t_rupees = max_t * lot_size
    max_t_rupees = round(max_t_rupees, 2)
    if legs[0]['trading_instrument'] == 1:
        min_t_rupees = min_t * lot_size    
    else:
        min_t_rupees = min_t * lot_size
    min_t_rupees = round(min_t_rupees, 2)

    winning_trades = len(tradepnl[tradepnl >= 0])
    losing_trades = len(tradepnl[tradepnl < 0])
    tradewise_accuracy = "{:.2f}".format((winning_trades / len(tradepnl)) * 100)

    max_win_streak = max_len
    max_loss_streak = max_len1
    returns_dd_ratio = "{:.2f}".format((sum(tradepnl) / trade_wise_dd)*(-1))
    expectancy_ratio = "{:.2f}".format(expectancy_ratio)
    expectancy_ratio1 = "{:.2f}".format(expectancy_ratio1)
    trade_wise_dd = "{:.2f}".format(trade_wise_dd)
    trade_wise_dd = float(trade_wise_dd)

    if legs[0]['trading_instrument'] == 1:
        trade_wise_dd_rupees = trade_wise_dd * lot_size    
    else:
        trade_wise_dd_rupees = trade_wise_dd * lot_size
    trade_wise_dd_rupees = float(trade_wise_dd_rupees)
    trade_wise_dd_rupees = round(trade_wise_dd_rupees, 2)



    rounded_avg_profit_winning_days= float(format(avg_profit_winning_days, '.2f'))
    rounded_avg_profit_winning_trades= float(format(avg_profit_winning_trades, '.2f'))
    rounded_avg_loss_lossing_days= float(format(avg_loss_lossing_days, '.2f'))
    rounded_avg_loss_lossing_trades= float(format(avg_loss_lossing_trades, '.2f'))

    def image_to_base64(image_path):
            try:
                if image_path.startswith(('http://', 'https://')):
                    response = requests.get(image_path)
                    response.raise_for_status()  # Raise an HTTPError for bad responses

                    # changehere
                    print(f"Content-Type: {response.headers['Content-Type']}\n")
                    print(f"Content-Length: {response.headers['Content-Length']}\n")
                    print(f"Status Code: {response.status_code}\n")

                    img = Image.open(BytesIO(response.content))
                else:
                    # If the image_path is a local file path
                    img = Image.open(image_path)

                buffer = BytesIO()
                img.save(buffer, format="png")
                image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                return image_base64
            except Exception as e:
                # Handle exceptions or log errors as needed
                # changehere
                print(f"Error processing image: {e}")

    for leg in legs:
        if leg['trailingsl'] == False:
            leg['sl_point'] = 0
            leg['tr_point'] = 0

        # if leg['re_entry_sl'] == False:
        #     leg['re_entry_times'] = 0

        # if leg['mtm_sl'] == False: 
        #     leg['mtm_sl_points'] = 0

    img1 = "files/images/ezquant_logo.jpg"
    img2 = "files/images/Z logo.png"
    # img1 = "https://lh3.googleusercontent.com/drive-viewer/AEYmBYSDa0M_uMXeaAWDEuLngEpJZlbXsSvJ69SZIAIx1t0PyJ_oFEGKUZ7b74BdVHvBK_V5B6fgKwOThuqTQRZ0Wy7ku8r5cQ=s1600"
    # img2 = "https://lh3.googleusercontent.com/drive-viewer/AEYmBYR80xPiU1q48KdVL2XerUz0teHXBRhBMnT6UNvCMdh_FgOmwG1p9DMk5rNU3bW4vXAMbqiXWF8_aZ8HmuUs4h0qXQVirA=s1600"

    img1_base64 = image_to_base64(img1)
    img2_base64 = image_to_base64(img2)
    leg_instrument1 = 0
    leg_instrument2 = 0
    temp_var = ""

    leg_data = []
    counter3 = 0
    for leg in legs:
        counter3 += 1
        leg_entry = {}

        for key, value in leg.items():
            variable_name = f"leg_{key}{counter3}" 
            exec(f"{variable_name} = '{value}'")
            leg_entry[key] = eval(variable_name)
        leg_data.append(leg_entry)

    # for leg in legs:
    #     if leg['mtm_sl'] == True:


    from jinja2 import Environment, FileSystemLoader

    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    #PATH
    template = env.get_template('backtest/files/Template/Backtester Template.html')
    trade_types_list = []
    diff_entries_list = []
    index_names_list = []
    option_type_list = []
    start_time_list = []
    end_time_list = []
    instrument_product_list = []
    quantity_list = []
    target_list = []
    stoploss_list = []
    trailing_stoploss_list = []
    trailing_tg_x_list = []
    trailing_sl_y_list = []
    tr_selectiontype_list = []
    reentry_on_sl_list = []
    reentry_time_list = []
    reentry_on_target_list = []
    reexecute_list = []
    reexecute_on_sl_list_without_wandt = []
    reexecute_on_sl_list_with_wandt = []
    reexecute_on_target_list_without_wandt = []
    reexecute_on_target_list_with_wandt = []
    waitandtrade_list = []
    group_entry_list = []
    group_exit_list = []
    mtm_stop_loss_list = []
    mtm_target_list = []
    total_premium_exit_list = []
    group_exit_list = []
    mtm_sl_list = []
    mtm_sl_flag_list = []
    entrytype_list = []
    moneyness_list = []
    diffentry1_list = []
    diffentry_list = []
    closesttype_list = []
    sl_type_list = []
    target_type_list = []
    mtm_lock_profit_list = []
    profit_lock_points_list = []
    lock_x_points_list = []
    lock_y_points_list = []
    mtm_x_list = []
    mtm_y_list = []
    mtm_sl_flag = legs[0]['mtm_sl']
    mtm_target_flag = legs[0]['mtm_target']
    mtm_sl_trail_flag = legs[0]['mtm_sl_trail']
    mtm_sl_trail_list = []
    waitntrade_list = []
    inc_decwt_list = []
    diff_wnt_list = []
    wnt_selectiontype_list = []
    re_execute_times_list = []
    re_execute_times_sl_list = []
    for i in range(1, counter3 + 1):
        index_names_list.append(eval(f'leg_trading_instrument{i}'))
        trade_types_list.append(eval(f'leg_tradetype{i}'))
        option_type_list.append(eval(f'leg_optiontype{i}'))
        diffentry_list.append(eval(f'leg_diffentry{i}'))
        closesttype_list.append(eval(f'leg_closesttype{i}'))
        start_time_list.append(eval(f'leg_entrytime{i}'))
        end_time_list.append(eval(f'leg_exittime{i}'))
        instrument_product_list.append(eval(f'leg_instrument_product{i}'))
        quantity_list.append(eval(f'leg_quantity{i}'))
        target_list.append(eval(f'leg_target_diff{i}'))
        stoploss_list.append(eval(f'leg_sl_diff{i}'))
        trailing_stoploss_list.append(eval(f'leg_trailingsl{i}'))
        trailing_tg_x_list.append(eval(f'leg_tr_point{i}'))
        trailing_sl_y_list.append(eval(f'leg_sl_point{i}'))
        tr_selectiontype_list.append(eval(f'leg_tr_selectiontype{i}'))
        reentry_on_sl_list.append(eval(f'leg_re_entry_sl{i}'))
        reentry_time_list.append(eval(f'leg_re_entry_times{i}'))
        reentry_on_target_list.append(eval(f'leg_re_entry_target{i}'))
        reexecute_list.append(eval(f'leg_re_execute{i}'))
        waitandtrade_list.append(eval(f'leg_waitntrade{i}'))
        # group_entry_list.append(eval(f'leg_{i}'))
        # group_exit_list.append(eval(f'leg_{i}'))
        # mtm_stop_loss_list.append(eval(f'leg_{i}'))
        # mtm_target_list.append(eval(f'leg_{i}'))
        total_premium_exit_list.append(eval(f'leg_total_premium_exit{i}'))
        mtm_sl_list.append(eval(f'leg_mtm_sl_points{i}'))
        # mtm_sl_flag_list.append(eval(f'leg_mtm_sl{i}'))
        entrytype_list.append(eval(f'leg_entrytype{i}'))
        moneyness_list.append(eval(f'leg_moneyness{i}'))
        diffentry1_list.append(eval(f'leg_diffentry1{i}'))
        sl_type_list.append(eval(f'leg_sl_type{i}'))
        target_type_list.append(eval(f'leg_target_type{i}'))
        mtm_lock_profit_list.append(eval(f'leg_mtm_lock_profit{i}'))
        profit_lock_points_list.append(eval(f'leg_profit_lock_points{i}'))
        if legs[0]['mtm_lock_profit'] == True:
            lock_x_points_list.append(eval(f'leg_lock_x_points{i}'))
            lock_y_points_list.append(eval(f'leg_lock_y_points{i}'))
        mtm_x_list.append(eval(f'leg_mtm_x{i}'))
        mtm_y_list.append(eval(f'leg_mtm_y{i}'))
        mtm_sl_trail_list.append(eval(f'leg_mtm_sl_trail{i}'))
        waitntrade_list.append(eval(f'leg_waitntrade{i}'))
        inc_decwt_list.append(eval(f'leg_inc_decwt{i}'))
        if legs[0]['waitntrade'] == True:
            diff_wnt_list.append(eval(f'leg_diff_wnt{i}'))
            wnt_selectiontype_list.append(eval(f'leg_wnt_selectiontype{i}'))
        re_execute_times_list.append(eval(f'leg_re_execute_times{i}'))
        re_execute_times_sl_list.append(eval(f'leg_re_execute_times_sl{i}'))
        # reexecute_on_sl_list_without_wandt.append(eval(f'leg_{i}'))
        # reexecute_on_sl_list_with_wandt.append(eval(f'leg_{i}'))
        # reexecute_on_target_list_without_wandt.append(eval(f'leg_{i}'))
        # reexecute_on_target_list_with_wandt.append(eval(f'leg_{i}'))

    print(profit_lock_points_list, "profit_lock_points_list")
    print(lock_x_points_list, "lock_x_points_list")
    print(lock_y_points_list, "lock_y_points_list")
    # lock_y_points_list = as

    if legs[0]['trading_instrument'] == 1:
        lock_sl_temp = lot_size * lock_sl_temp
        profit_lock_points_list = [int(float(num)) * lot_size for num in profit_lock_points_list]
        lock_x_points_list = [int(float(num)) * lot_size for num in lock_x_points_list]
        lock_y_points_list = [int(float(num)) * lot_size for num in lock_y_points_list]

        # profit_lock_points_list = [lot_size * int(value) for value in profit_lock_points_list]
        # lock_x_points_list = [lot_size * int(value) for value in lock_x_points_list]
        # lock_y_points_list = [lot_size * int(value) for value in lock_y_points_list]
    else:
        lock_sl_temp = lot_size * lock_sl_temp
        profit_lock_points_list = [int(float(num)) * lot_size for num in profit_lock_points_list]
        lock_x_points_list = [int(float(num)) * lot_size for num in lock_x_points_list]
        lock_y_points_list = [int(float(num)) * lot_size for num in lock_y_points_list]
        # profit_lock_points_list = [50 * int(value) for value in profit_lock_points_list]
        # lock_x_points_list = [50 * int(value) for value in lock_x_points_list]
        # lock_y_points_list = [50 * int(value) for value in lock_y_points_list]


        # diff_entries_list.append(eval(f'leg_diffentry{i}'))

    comparison_data = zip(diffentry_list, closesttype_list)
    comparison_data2 = zip(entrytype_list, moneyness_list)
    comparison_data3 = zip(entrytype_list, diffentry1_list, moneyness_list)
    comparison_data4 = zip(stoploss_list, sl_type_list)
    comparison_data5 = zip(target_list, target_type_list)

    comparison_data6 = zip(trailing_tg_x_list, tr_selectiontype_list)
    comparison_data7 = zip(trailing_sl_y_list, tr_selectiontype_list)
    
    comparison_data8 = zip(diff_wnt_list, wnt_selectiontype_list)


    trailing_stoploss_auto = any(value == 'True' for value in trailing_stoploss_list)
    reentry_sl_auto = any(value == 'True' for value in reentry_on_sl_list)
    reentry_tg_auto = any(value == 'True' for value in reentry_on_target_list)
    lock_n_trail_auto = any(value == 'True' for value in mtm_lock_profit_list)
    wandt_auto = any(value == 'True' for value in waitntrade_list)
    reexecute_auto = any(value == 'True' for value in re_execute_times_list)
    

    if __name__ == "__main__":
        txt_name = txt_name
        # net_profit = net_profit
        # net_profit_points = net_profit_points
        with open(txt_name, 'r') as file:
            output_content = file.read()
    with open(txt_name, 'r') as file:
            output_content = file.read()
    date_list_2018 = [rounded_monday_2018, rounded_tuesday_2018, rounded_wednesday_2018, rounded_thursday_2018, rounded_friday_2018]
    date_list_2019 = [rounded_monday_2019, rounded_tuesday_2019, rounded_wednesday_2019, rounded_thursday_2019, rounded_friday_2019]
    date_list_2020 = [rounded_monday_2020, rounded_tuesday_2020, rounded_wednesday_2020, rounded_thursday_2020, rounded_friday_2020]
    date_list_2021 = [rounded_monday_2021, rounded_tuesday_2021, rounded_wednesday_2021, rounded_thursday_2021, rounded_friday_2021]
    date_list_2022 = [rounded_monday_2022, rounded_tuesday_2022, rounded_wednesday_2022, rounded_thursday_2022, rounded_friday_2022]
    date_list_2023 = [rounded_monday_2023, rounded_tuesday_2023, rounded_wednesday_2023, rounded_thursday_2023, rounded_friday_2023]

    date_value_2018 = any(value != 0 for value in date_list_2018)
    date_value_2019 = any(value != 0 for value in date_list_2019)
    date_value_2020 = any(value != 0 for value in date_list_2020)
    date_value_2021 = any(value != 0 for value in date_list_2021)
    date_value_2022 = any(value != 0 for value in date_list_2022)
    date_value_2023 = any(value != 0 for value in date_list_2023)

    month_list_2018 = [rounded_january_2018, rounded_february_2018, rounded_march_2018, rounded_april_2018, rounded_may_2018, rounded_june_2018, rounded_july_2018, rounded_august_2018, rounded_september_2018, rounded_october_2018, rounded_november_2018, rounded_december_2018]
    month_list_2019 = [rounded_january_2019, rounded_february_2019, rounded_march_2019, rounded_april_2019, rounded_may_2019, rounded_june_2019, rounded_july_2019, rounded_august_2019, rounded_september_2019, rounded_october_2019, rounded_november_2019, rounded_december_2019]
    month_list_2020 = [rounded_january_2020, rounded_february_2020, rounded_march_2020, rounded_april_2020, rounded_may_2020, rounded_june_2020, rounded_july_2020, rounded_august_2020, rounded_september_2020, rounded_october_2020, rounded_november_2020, rounded_december_2020]
    month_list_2021 = [rounded_january_2021, rounded_february_2021, rounded_march_2021, rounded_april_2021, rounded_may_2021, rounded_june_2021, rounded_july_2021, rounded_august_2021, rounded_september_2021, rounded_october_2021, rounded_november_2021, rounded_december_2021]
    month_list_2022 = [rounded_january_2022, rounded_february_2022, rounded_march_2022, rounded_april_2022, rounded_may_2022, rounded_june_2022, rounded_july_2022, rounded_august_2022, rounded_september_2022, rounded_october_2022, rounded_november_2022, rounded_december_2022]
    month_list_2023 = [rounded_january_2023, rounded_february_2023, rounded_march_2023, rounded_april_2023, rounded_may_2023, rounded_june_2023, rounded_july_2023, rounded_august_2023, rounded_september_2023, rounded_october_2023, rounded_november_2023, rounded_december_2023]
    
    month_value_2018 = any(value != 0 for value in month_list_2018)
    month_value_2019 = any(value != 0 for value in month_list_2019) 
    month_value_2020 = any(value != 0 for value in month_list_2020)
    month_value_2021 = any(value != 0 for value in month_list_2021)
    month_value_2022 = any(value != 0 for value in month_list_2022)
    month_value_2023 = any(value != 0 for value in month_list_2023)

    output = template.render(
        dff1 = dff1,
        dff2 = dff2,
        trailing_stoploss_auto = trailing_stoploss_auto,
        reentry_sl_auto = reentry_sl_auto,
        reentry_tg_auto = reentry_tg_auto,
        wandt_auto = wandt_auto,
        lock_n_trail_auto = lock_n_trail_auto,
        reexecute_auto = reexecute_auto,

        lock_sl_temp = lock_sl_temp,
        inc_decwt_list = inc_decwt_list,
        waitntrade_list = waitntrade_list,
        diff_wnt_list = diff_wnt_list,
        wnt_selectiontype_list = wnt_selectiontype_list,
        re_execute_times_list = re_execute_times_list,
        re_execute_times_sl_list = re_execute_times_sl_list,

        mtm_target_flag = mtm_target_flag,
        mtm_sl_trail_flag = mtm_sl_trail_flag,
        mtm_sl_trail_list = mtm_sl_trail_list,
        mtm_target_list = mtm_target_list,
        mtm_x_list = mtm_x_list,
        mtm_y_list = mtm_y_list,
        mtm_lock_profit_list = mtm_lock_profit_list,
        profit_lock_points_list = profit_lock_points_list,
        lock_x_points_list = lock_x_points_list,
        lock_y_points_list = lock_y_points_list,
        mtm_sl_flag = mtm_sl_flag,
        # mtm_sl_flag_list = mtm_sl_flag_list,
        avg_profit_winning_days_rupees = avg_profit_winning_days_rupees,
        avg_profit_winning_trades_rupees = avg_profit_winning_trades_rupees,
        avg_loss_lossing_days_rupees = avg_loss_lossing_days_rupees,
        avg_loss_lossing_trades_rupees = avg_loss_lossing_trades_rupees,
        day_wise_dd_rupees = day_wise_dd_rupees,
        avg_profit_per_day_rupees = avg_profit_per_day_rupees,
        max_tt_rupees = max_tt_rupees,
        min_tt_rupees = min_tt_rupees,
        avg_profit_per_trade_rupees = avg_profit_per_trade_rupees,
        trade_wise_dd_rupees = trade_wise_dd_rupees,
        max_t_rupees = max_t_rupees,
        min_t_rupees = min_t_rupees,

        rounded_avg_profit_winning_days = rounded_avg_profit_winning_days,
        rounded_avg_profit_winning_trades = rounded_avg_profit_winning_trades,
        rounded_avg_loss_lossing_days = rounded_avg_loss_lossing_days,
        rounded_avg_loss_lossing_trades = rounded_avg_loss_lossing_trades,
        avg_profit_winning_days = avg_profit_winning_days,
        avg_loss_lossing_days = avg_loss_lossing_days,
        max_t = max_t,
        min_t = min_t,
        avg_profit_winning_trades = avg_profit_winning_trades,
        avg_loss_lossing_trades = avg_loss_lossing_trades,
        max_tt = max_tt,
        min_tt = min_tt,
        comparison_data3 = comparison_data3,
        comparison_data4 = comparison_data4,
        comparison_data5 = comparison_data5,
        comparison_data6 = comparison_data6,
        comparison_data7 = comparison_data7,
        comparison_data8 = comparison_data8,
        mtm_sl_list = mtm_sl_list,
        diffentry1_list = diffentry1_list,
        comparison_data2 = comparison_data2,
        moneyness_list = moneyness_list,
        entrytype_list = entrytype_list,
        month_value_2018 = month_value_2018,
        month_value_2019 = month_value_2019,
        month_value_2020 = month_value_2020,
        month_value_2021 = month_value_2021,
        month_value_2022 = month_value_2022, 
        month_value_2023 = month_value_2023,
        date_value_2018 = date_value_2018,
        date_value_2019 = date_value_2019,
        date_value_2020 = date_value_2020,
        date_value_2021 = date_value_2021,
        date_value_2022 = date_value_2022,
        date_value_2023 = date_value_2023,

        comparison_data = comparison_data,
        output_content=output_content,
        counter3=counter3,
        index_names_list=index_names_list, 
        trade_types_list=trade_types_list, 
        option_type_list=option_type_list, 
        diffentry_list=diffentry_list, 
        closesttype_list=closesttype_list,
        start_time_list=start_time_list, 
        end_time_list=end_time_list, 
        instrument_product_list=instrument_product_list,
        quantity_list=quantity_list,
        target_list=target_list, 
        stoploss_list=stoploss_list, 
        trailing_stoploss_list=trailing_stoploss_list,
        trailing_tg_x_list=trailing_tg_x_list,
        trailing_sl_y_list=trailing_sl_y_list,
        tr_selectiontype_list=tr_selectiontype_list,
        reentry_on_sl_list=reentry_on_sl_list, 
        reentry_time_list=reentry_time_list,
        reentry_on_target_list=reentry_on_target_list,
        reexecute_list=reexecute_list,
        waitandtrade_list=waitandtrade_list,
        total_premium_exit_list=total_premium_exit_list,

        trading_days=trading_days,
        avg_profit_per_day=avg_profit_per_day,
        winning_days=winning_days,
        losing_days=losing_days,
        daywise_accuracy=daywise_accuracy,
        num_trades=num_trades,
        avg_profit_per_trade=avg_profit_per_trade,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        tradewise_accuracy=tradewise_accuracy,
        max_win_streak=max_win_streak,
        max_loss_streak=max_loss_streak,
        returns_dd_ratio=returns_dd_ratio,
        expectancy_ratio=expectancy_ratio,
        expectancy_ratio1=expectancy_ratio1,
        day_wise_dd=day_wise_dd,
        trade_wise_dd=trade_wise_dd,

        rounded_monday_2018=rounded_monday_2018,
        rounded_tuesday_2018=rounded_tuesday_2018,
        rounded_wednesday_2018=rounded_wednesday_2018,
        rounded_thursday_2018=rounded_thursday_2018,
        rounded_friday_2018=rounded_friday_2018,

        rounded_monday_2019=rounded_monday_2019,
        rounded_tuesday_2019=rounded_tuesday_2019,
        rounded_wednesday_2019=rounded_wednesday_2019,
        rounded_thursday_2019=rounded_thursday_2019,
        rounded_friday_2019=rounded_friday_2019,
        
        rounded_monday_2020=rounded_monday_2020,
        rounded_tuesday_2020=rounded_tuesday_2020,
        rounded_wednesday_2020=rounded_wednesday_2020,
        rounded_thursday_2020=rounded_thursday_2020,
        rounded_friday_2020=rounded_friday_2020,

        rounded_monday_2021=rounded_monday_2021,
        rounded_tuesday_2021=rounded_tuesday_2021,
        rounded_wednesday_2021=rounded_wednesday_2021,
        rounded_thursday_2021=rounded_thursday_2021,
        rounded_friday_2021=rounded_friday_2021,

        rounded_monday_2022=rounded_monday_2022,
        rounded_tuesday_2022=rounded_tuesday_2022,
        rounded_wednesday_2022=rounded_wednesday_2022,
        rounded_thursday_2022=rounded_thursday_2022,
        rounded_friday_2022=rounded_friday_2022,

        rounded_monday_2023=rounded_monday_2023,
        rounded_tuesday_2023=rounded_tuesday_2023,
        rounded_wednesday_2023=rounded_wednesday_2023,
        rounded_thursday_2023=rounded_thursday_2023,
        rounded_friday_2023=rounded_friday_2023,
        net_profit = net_profit,
        net_profit_points = net_profit_points,
        pnl_d = pnl_d,
        tradepnl = tradepnl,

        rounded_monday_roi_2018 = rounded_monday_roi_2018,
        rounded_tuesday_roi_2018 = rounded_tuesday_roi_2018,
        rounded_wednesday_roi_2018 = rounded_wednesday_roi_2018,
        rounded_thursday_roi_2018 = rounded_thursday_roi_2018,
        rounded_friday_roi_2018 = rounded_friday_roi_2018,

        rounded_monday_roi_2019 = rounded_monday_roi_2019,
        rounded_tuesday_roi_2019 = rounded_tuesday_roi_2019,
        rounded_wednesday_roi_2019 = rounded_wednesday_roi_2019,
        rounded_thursday_roi_2019 = rounded_thursday_roi_2019,
        rounded_friday_roi_2019 = rounded_friday_roi_2019,

        rounded_monday_roi_2020 = rounded_monday_roi_2020,
        rounded_tuesday_roi_2020 = rounded_tuesday_roi_2020,
        rounded_wednesday_roi_2020 = rounded_wednesday_roi_2020,
        rounded_thursday_roi_2020 = rounded_thursday_roi_2020,
        rounded_friday_roi_2020 = rounded_friday_roi_2020,

        rounded_monday_roi_2021 = rounded_monday_roi_2021,
        rounded_tuesday_roi_2021 = rounded_tuesday_roi_2021,
        rounded_wednesday_roi_2021 = rounded_wednesday_roi_2021,
        rounded_thursday_roi_2021 = rounded_thursday_roi_2021,
        rounded_friday_roi_2021 = rounded_friday_roi_2021,

        rounded_monday_roi_2022 = rounded_monday_roi_2022,
        rounded_tuesday_roi_2022 = rounded_tuesday_roi_2022,
        rounded_wednesday_roi_2022 = rounded_wednesday_roi_2022,
        rounded_thursday_roi_2022 = rounded_thursday_roi_2022,
        rounded_friday_roi_2022 = rounded_friday_roi_2022,

        rounded_monday_roi_2023 = rounded_monday_roi_2023,
        rounded_tuesday_roi_2023 = rounded_tuesday_roi_2023,
        rounded_wednesday_roi_2023 = rounded_wednesday_roi_2023,
        rounded_thursday_roi_2023 = rounded_thursday_roi_2023,
        rounded_friday_roi_2023 = rounded_friday_roi_2023,

        daywise_chart=image_base64,
        tradewise_chart=trade_image_base64,

        rounded_january_2018   = rounded_january_2018,
        rounded_february_2018  = rounded_february_2018,
        rounded_march_2018     = rounded_march_2018, 
        rounded_april_2018     = rounded_april_2018,
        rounded_may_2018       = rounded_may_2018,
        rounded_june_2018      = rounded_june_2018, 
        rounded_july_2018      = rounded_july_2018,
        rounded_august_2018    = rounded_august_2018,
        rounded_september_2018 = rounded_september_2018,
        rounded_october_2018   = rounded_october_2018,
        rounded_november_2018  = rounded_november_2018,
        rounded_december_2018  = rounded_december_2018,

        rounded_january_2019   = rounded_january_2019,
        rounded_february_2019  = rounded_february_2019,
        rounded_march_2019     = rounded_march_2019, 
        rounded_april_2019     = rounded_april_2019,
        rounded_may_2019       = rounded_may_2019,
        rounded_june_2019      = rounded_june_2019, 
        rounded_july_2019      = rounded_july_2019,
        rounded_august_2019    = rounded_august_2019,
        rounded_september_2019 = rounded_september_2019,
        rounded_october_2019   = rounded_october_2019,
        rounded_november_2019  = rounded_november_2019,
        rounded_december_2019  = rounded_december_2019,

        rounded_january_2020   = rounded_january_2020,
        rounded_february_2020  = rounded_february_2020,
        rounded_march_2020     = rounded_march_2020, 
        rounded_april_2020     = rounded_april_2020,
        rounded_may_2020       = rounded_may_2020,
        rounded_june_2020      = rounded_june_2020, 
        rounded_july_2020      = rounded_july_2020,
        rounded_august_2020    = rounded_august_2020,
        rounded_september_2020 = rounded_september_2020,
        rounded_october_2020   = rounded_october_2020,
        rounded_november_2020  = rounded_november_2020,
        rounded_december_2020  = rounded_december_2020,

        rounded_january_2021   = rounded_january_2021,
        rounded_february_2021  = rounded_february_2021,
        rounded_march_2021     = rounded_march_2021, 
        rounded_april_2021     = rounded_april_2021,
        rounded_may_2021       = rounded_may_2021,
        rounded_june_2021      = rounded_june_2021, 
        rounded_july_2021      = rounded_july_2021,
        rounded_august_2021    = rounded_august_2021,
        rounded_september_2021 = rounded_september_2021,
        rounded_october_2021   = rounded_october_2021,
        rounded_november_2021  = rounded_november_2021,
        rounded_december_2021  = rounded_december_2021,

        rounded_january_2022   = rounded_january_2022,
        rounded_february_2022  = rounded_february_2022,
        rounded_march_2022     = rounded_march_2022, 
        rounded_april_2022     = rounded_april_2022,
        rounded_may_2022       = rounded_may_2022,
        rounded_june_2022      = rounded_june_2022, 
        rounded_july_2022      = rounded_july_2022,
        rounded_august_2022    = rounded_august_2022,
        rounded_september_2022 = rounded_september_2022,
        rounded_october_2022   = rounded_october_2022,
        rounded_november_2022  = rounded_november_2022,
        rounded_december_2022  = rounded_december_2022,

        rounded_january_2023   = rounded_january_2023,
        rounded_february_2023  = rounded_february_2023,
        rounded_march_2023     = rounded_march_2023, 
        rounded_april_2023     = rounded_april_2023,
        rounded_may_2023       = rounded_may_2023,
        rounded_june_2023      = rounded_june_2023, 
        rounded_july_2023      = rounded_july_2023,
        rounded_august_2023    = rounded_august_2023,
        rounded_september_2023 = rounded_september_2023,
        rounded_october_2023   = rounded_october_2023,
        rounded_november_2023  = rounded_november_2023,
        rounded_december_2023  = rounded_december_2023,
        
        rounded_january_roi_2018   = rounded_january_roi_2018,
        rounded_february_roi_2018  = rounded_february_roi_2018,
        rounded_march_roi_2018     = rounded_march_roi_2018, 
        rounded_april_roi_2018     = rounded_april_roi_2018, 
        rounded_may_roi_2018       = rounded_may_roi_2018,
        rounded_june_roi_2018      = rounded_june_roi_2018, 
        rounded_july_roi_2018      = rounded_july_roi_2018,
        rounded_august_roi_2018    = rounded_august_roi_2018,
        rounded_september_roi_2018 = rounded_september_roi_2018,
        rounded_october_roi_2018   = rounded_october_roi_2018,
        rounded_november_roi_2018  = rounded_november_roi_2018,
        rounded_december_roi_2018  = rounded_december_roi_2018,

        rounded_january_roi_2019   = rounded_january_roi_2019,
        rounded_february_roi_2019  = rounded_february_roi_2019,
        rounded_march_roi_2019     = rounded_march_roi_2019, 
        rounded_april_roi_2019     = rounded_april_roi_2019, 
        rounded_may_roi_2019       = rounded_may_roi_2019,
        rounded_june_roi_2019      = rounded_june_roi_2019, 
        rounded_july_roi_2019      = rounded_july_roi_2019,
        rounded_august_roi_2019    = rounded_august_roi_2019,
        rounded_september_roi_2019 = rounded_september_roi_2019,
        rounded_october_roi_2019   = rounded_october_roi_2019,
        rounded_november_roi_2019  = rounded_november_roi_2019,
        rounded_december_roi_2019  = rounded_december_roi_2019,

        rounded_january_roi_2020   = rounded_january_roi_2020,
        rounded_february_roi_2020  = rounded_february_roi_2020,
        rounded_march_roi_2020     = rounded_march_roi_2020, 
        rounded_april_roi_2020     = rounded_april_roi_2020, 
        rounded_may_roi_2020       = rounded_may_roi_2020,
        rounded_june_roi_2020      = rounded_june_roi_2020, 
        rounded_july_roi_2020      = rounded_july_roi_2020,
        rounded_august_roi_2020    = rounded_august_roi_2020,
        rounded_september_roi_2020 = rounded_september_roi_2020,
        rounded_october_roi_2020   = rounded_october_roi_2020,
        rounded_november_roi_2020  = rounded_november_roi_2020,
        rounded_december_roi_2020  = rounded_december_roi_2020,
        

        rounded_january_roi_2021   = rounded_january_roi_2021,
        rounded_february_roi_2021  = rounded_february_roi_2021,
        rounded_march_roi_2021     = rounded_march_roi_2021, 
        rounded_april_roi_2021     = rounded_april_roi_2021, 
        rounded_may_roi_2021       = rounded_may_roi_2021,
        rounded_june_roi_2021      = rounded_june_roi_2021, 
        rounded_july_roi_2021      = rounded_july_roi_2021,
        rounded_august_roi_2021    = rounded_august_roi_2021,
        rounded_september_roi_2021 = rounded_september_roi_2021,
        rounded_october_roi_2021   = rounded_october_roi_2021,
        rounded_november_roi_2021  = rounded_november_roi_2021,
        rounded_december_roi_2021  = rounded_december_roi_2021,
        
        rounded_january_roi_2022   = rounded_january_roi_2022,
        rounded_february_roi_2022  = rounded_february_roi_2022,
        rounded_march_roi_2022     = rounded_march_roi_2022, 
        rounded_april_roi_2022     = rounded_april_roi_2022, 
        rounded_may_roi_2022       = rounded_may_roi_2022,
        rounded_june_roi_2022      = rounded_june_roi_2022, 
        rounded_july_roi_2022      = rounded_july_roi_2022,
        rounded_august_roi_2022    = rounded_august_roi_2022,
        rounded_september_roi_2022 = rounded_september_roi_2022,
        rounded_october_roi_2022   = rounded_october_roi_2022,
        rounded_november_roi_2022  = rounded_november_roi_2022,
        rounded_december_roi_2022  = rounded_december_roi_2022,
        
        rounded_january_roi_2023   = rounded_january_roi_2023,
        rounded_february_roi_2023  = rounded_february_roi_2023,
        rounded_march_roi_2023     = rounded_march_roi_2023, 
        rounded_april_roi_2023     = rounded_april_roi_2023, 
        rounded_may_roi_2023       = rounded_may_roi_2023,
        rounded_june_roi_2023      = rounded_june_roi_2023, 
        rounded_july_roi_2023      = rounded_july_roi_2023,
        rounded_august_roi_2023    = rounded_august_roi_2023,
        rounded_september_roi_2023 = rounded_september_roi_2023,
        rounded_october_roi_2023   = rounded_october_roi_2023,
        rounded_november_roi_2023  = rounded_november_roi_2023,
        rounded_december_roi_2023  = rounded_december_roi_2023,

        rounded_max_un_pr = rounded_max_un_pr,
        rounded_max_un_ls = rounded_max_un_ls,


        data_length=data_length, 
        datee = datee,
        rounded_pnl_d = rounded_pnl_d,
        expiry_day = expiry_day,
        trades = trades,
        per_change_max_column = per_change_max_column,
        per_change_min_column = per_change_min_column,
        per_change_close_column = per_change_close_column,
        rounded_cumulative_pnl = rounded_cumulative_pnl,

        trade_day=trade_day, 
        trade_dt=trade_dt, 
        trade_exp=trade_exp, 
        trade_typel=trade_typel, 
        instrument=instrument, 
        entry_t=entry_t, 
        entry_p=entry_p, 
        exit_t=exit_t, 
        exit_p=exit_p, 
        rounded_tradepnl=rounded_tradepnl, 
        rounded_max_run_up_profit=rounded_max_run_up_profit, 
        rounded_max_run_up_loss=rounded_max_run_up_loss, 
        data_length2=data_length2, 
        img1 = img1_base64,
        img2 = img2_base64,


    )
    # with open('E:/EzQuant/django backtesting/django backtesting/Backtesting/files/output.html', 'w') as file:
    #PATH
    with open(f"backtest/files/HTML/2.html", 'w') as file:
    # with open(f"backtest/files/HTML/Only_Expiry_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}.html", 'w') as file:
        file.write(output)
        # changehere
    print("HTML file generated successfully.")


            # html_file_path = f"E:/EzQuant/Data/Backtesting_data/HTML pages/Only_Expiry_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.html"


############################################# For Server #############################################

    def html_to_pdf(html_file_path, output_pdf_path):
        try:
            try:
                # pdf_content = pdfkit.from_file(html_file_path, configuration=pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf'))
                # pdf_content = pdfkit.from_file(html_file_path, configuration=pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf'))
                pdf_content = pdfkit.from_file(html_file_path, configuration=pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'))
                # pdfkit.from_file(html_file_path, configuration=pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'))
                print("PDF Generated Successfully.")
                # print(pdf_content)
                return pdf_content
            except Exception as e:
                return e
        except Exception as e:
            return Response(f'Error in line 8013, {e}' )
            
############################################# For Server #############################################




    # def html_to_pdf(html_file_path, output_pdf_path):

    #     try:
    #         pdfkit.from_file(html_file_path, output_pdf_path, configuration=pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf'))
    #         # pdfkit.from_file(html_file_path, output_pdf_path, configuration=pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'))
    #     except Exception as e:
    #         pass


    for leg in legs:
        leg['entrytime']=str(leg['entrytime'])
        leg['exittime']=str(leg['exittime'])
    #####################################################
    # html_file = f"E:/EzQuant/Data/Backtesting_data/HTML pages/Only_Expiry_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.html"
    #PATH
    # html_file = f"backtest/files/HTML/Only_Expiry_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}.html"
    html_file = f"backtest/files/HTML/2.html"
    pdf_file = f"backtest/files/Output/2.pdf"
    # html_file = "E:/EzQuant/django backtesting/django backtesting/Backtesting/files/template1.html"
    # pdf_file = f"E:/EzQuant/Data/Backtesting_data/PDF Outputs/BNF/Only_Expiry_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
    # pdf_file = f"backtest/files/Output/1.html"
    # html_to_pdf(html_file, pdf_file)
    mail_flag = False
    if request.method == 'POST':

        pdf_file = f"backtest/files/Output/2.pdf"
        html_file_path = html_file
        pdf_file_path = f"backtest/files/Output/2.pdf"
        
        pdf_content = html_to_pdf(html_file_path, pdf_file_path)
        print(pdf_content, "pdf_content")
        if pdf_content:
            # print(pdf_content, 'hiiiiiiiiiiiiiiiiiiiiiiiii')
            # backtest_result = BacktestResult(pdf_file=pdf_content)
            backtest_result = BacktestResult(pdf_file=pdf_content, user=request.user)
            backtest_result.save()
            pdf_file_path = f'{pdf_file_path}'
        print(backtest_result, "backtest_result")
            # try:
            #     with open(pdf_file_path, 'wb') as pdf:
            #         pdf.write(pdf_content)
            #         response = HttpResponse(pdf_content, content_type='application/pdf')
            #         response['Content-Disposition'] = f'inline; filename={pdf_file_path}'
            #         # return response
            # except Exception as e:
            #     return HttpResponse("PDF file not found", status=404)
        print(request.user)
        print(backtest_result.id)
        def send_pdf_via_email(backtest_result_id, from_email, to_email):
            # backtest_result = BacktestResult.objects.get(pk=backtest_result_id)
            backtest_result = BacktestResult.objects.get(pk=backtest_result_id, user=request.user)

            pdf_data = backtest_result.pdf_file

            subject = 'Backtest Result PDF'
            body = 'Please find the backtest result attached.'

            email = EmailMessage(subject, body, from_email, [to_email])

            email.attach(f'backtest_result_{backtest_result.pk}.pdf', pdf_data, 'application/pdf')

            email.send()
            mail_flag = True
        send_pdf_via_email(backtest_result_id=backtest_result.id, from_email='abhiezquant@gmail.com', to_email=request.user)
        # send_pdf_via_email(backtest_result_id=backtest_result.id, from_email='abhiezquant@gmail.com', to_email='abhichuiya@gmail.com')

        if mail_flag == True:
            backtest_result.delete()

        # def save_pdf_to_backtest_result(pdf_file, file_name):
        #     backtest_result = BacktestResult()

        #     backtest_result.pdf_file.save(file_name, ContentFile(pdf_file.read()), save=True)

        #     backtest_result.save()


    # #PATH
    # if legs[0]['trading_instrument'] == 1:
    #     if dayy == ["Thursday"]:
    #         pdf_file = f"backtest/files/Output/Only_Expiry_BNF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
    #     elif dayy == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
    #         pdf_file = f"backtest/files/Output/Everyday_BNF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
    #     else:
    #         pdf_file = ""

    #         for i in dayy:
    #             pdf_file += f"{i}_"

    #         pdf_file = pdf_file[:-1]
    #         pdf_file = f"backtest/Output/{pdf_file}_BNF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
    # if legs[0]['trading_instrument'] == 2:
    #     if dayy == ["Thursday"]:
    #         pdf_file = f"backtest/files/Output/Only_Expiry_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
    #     elif dayy == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
    #         pdf_file = f"backtest/files/Output/Everyday_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
    #     else:
    #         pdf_file = ""

    #         for i in dayy:
    #             pdf_file += f"{i}_"

    #         pdf_file = pdf_file[:-1]
    #         pdf_file = f"backtest/files/Output/{pdf_file}_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
    #         # pdf_file = f"E:/EzQuant/Lock and Trail/NF Outputs/{pdf_file}_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
    # if legs[0]['trading_instrument'] == 3:
        # if dayy == ["Thursday"]:
        #     pdf_file = f"E:/EzQuant/Data/Backtesting_data/PDF Outputs/FNF/Only_Expiry_FNF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
        # elif dayy == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        #     pdf_file = f"E:/EzQuant/Data/Backtesting_data/PDF Outputs/FNF/Everyday_FNF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
        # else:
        #     pdf_file = ""

        #     for i in dayy:
        #         pdf_file += f"{i}_"

        #     pdf_file = pdf_file[:-1]
        #     pdf_file = f"E:/EzQuant/Data/Backtesting_data/PDF Outputs/FNF/{pdf_file}_FNF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.pdf"
        #  = f"E:/EzQuant/Data/Backtesting_data/PDF Outputs/{pdf_file} BNF.pdf"

    # pdf_file = f"backtest/files/1.pdf"
    html_to_pdf(html_file, pdf_file)


    #PATH
    # html_file_path = f"Only_Expiry_NF_ReEntry{legs[0]['re_entry_times']}_{legs[1]['re_entry_times']}_SL_Diff_{legs[0]['sl_diff']},{legs[1]['sl_diff']}_Premium_Type_{legs[0]['diffentry']}_{legs[0]['closesttype']}_{legs[1]['diffentry']}_{legs[1]['closesttype']}_EntryTime_{legs[0]['entrytime'].replace(':', '_')}_{legs[1]['entrytime'].replace(':', '_')}_ExitTime_{legs[0]['exittime'].replace(':', '_')}_{legs[1]['exittime'].replace(':', '_')}.html"
    # import json
    # (legs)
    # def create_json(summary_report):
    #     return json.dumps(summary_report, indent=4)
    # if legs[0]['trading_instrument'] == 1:
    #     indexx = "BANK NIFTY"
    # elif legs[0]['trading_instrument'] == 2:
    #     indexx = "NIFTY"
    # elif legs[0]['trading_instrument'] == 3:
    #     indexx = "FIN NIFTY"
    # desc_report = {
    #     "leg1": {
    #         "Index": indexx,
    #         "Expiry": "Weekly",
    #         "Trade Type": legs[0]['tradetype'],
    #         "Option Type": f"{legs[0]['optiontype']}",
    #         "Strike Selection": f"Less than {legs[0]['diffentry']}",
    #         "Start Time": f"{legs[0]['entrytime']}",
    #         "End Time": f"{legs[0]['exittime']}",
    #         "Instrument Product": f"{legs[0]['instrument_product']}",
    #         "Quantity": f"{legs[0]['quantity']}",
    #         "Target": f"{legs[0]['target_flag']}",
    #         "Stop Loss": f"{legs[0]['sl_diff']}%",
    #         "Trailing Stop Loss": f"{legs[0]['trailingsl']}",
    #         "ReEntry On SL": f"{legs[0]['re_entry_sl']}",
    #         "ReEntry Times": f"{legs[0]['re_entry_times']}",
    #         "ReEntry On Target": f"{legs[0]['re_entry_target']}",
    #         "ReExecute": f"{legs[0]['re_execute']}",
    #         "Wait & Trade": f"{legs[0]['waitntrade']}",
    #         "Group Entry": f"False",
    #         "Group Exit": f"False",
    #         "MTM Stop Loss": f"{mtm_sl_points}",
    #         "MTM Target": f"{legs[0]['mtm_target']}",
    #         "Total Premium Exit": f"{legs[0]['total_premium_exit']}"

    #     },
    #     "leg2": {
    #         "Index": indexx,
    #         "Expiry": "Weekly",
    #         "Trade Type": f"{legs[1]['tradetype']}",
    #         "Option Type": f"{legs[1]['optiontype']}",
    #         "Strike Selection": f"Less than {legs[1]['diffentry']}",
    #         "Start Time": f"{legs[1]['entrytime']}",
    #         "End Time": f"{legs[1]['exittime']}",
    #         "Instrument Product": f"{legs[1]['instrument_product']}",
    #         "Quantity": f"{legs[1]['quantity']}",
    #         "Target": f"{legs[1]['target_flag']}",
    #         "Stop Loss": f"{legs[1]['sl_diff']}%",
    #         "Trailing Stop Loss": f"{legs[1]['trailingsl']}",
    #         "ReEntry On SL": f"{legs[1]['re_entry_sl']}",
    #         "ReEntry Times": f"{legs[1]['re_entry_times']}",
    #         "ReEntry On Target": f"{legs[1]['re_entry_target']}",
    #         "ReExecute": f"{legs[1]['re_execute']}",
    #         "Wait & Trade": f"{legs[1]['waitntrade']}",
    #         "Group Entry": f"False",
    #         "Group Exit": f"False",
    #         "MTM Stop Loss": f"{mtm_sl_points}",
    #         "MTM Target": f"{legs[1]['mtm_target']}",
    #         "Total Premium Exit": f"{legs[1]['total_premium_exit']}"


    #     }
    # }
    # #changehere
    # desc_report_object = create_json(desc_report)
    # print(desc_report_object)

    # summary_report = {
    #     "estimated_margin_requirement": "100000 Rs.",
    #     "net_profit_loss": f"{ net_profit_points} Rs. ({ net_profit } Points)",
    #     "number_of_trading_days": f"{trading_days} Days",
    #     "average_profit_per_day": f"{ avg_profit_per_day_rupees } Rs. ({ avg_profit_per_day } Points)",

    #     "maximum_trade_profit": f"{ max_tt_rupees } Rs. ({ max_tt } Points)",
    #     "maximum_trade_loss": f"{ min_tt_rupees } Rs. ({ min_tt } Points)",


    #     "number_of_winning_days": f"{winning_days} Days",
    #     "number_of_losing_days": f"{losing_days} Days",

    #     "day_wise_accuracy": f"{daywise_accuracy}%",
    #     "number_of_trades": f"{num_trades} Trades",
    #     "average_profit_per_trade": f"{ avg_profit_per_trade_rupees } Rs. ({ avg_profit_per_trade } Points)",
    #     "number_of_winning_trades": f"{winning_trades} Trades",
    #     "number_of_losing_trades": f"{losing_trades} Trades",

    #     "average_profit_on_winning_days": f"{ avg_profit_winning_days_rupees } Rs. ({ rounded_avg_profit_winning_days } Points)",
    #     "average_loss_on_losing_days": f"{ avg_loss_lossing_days_rupees } Rs. ({ rounded_avg_loss_lossing_days } Points)",
    #     "average_profit_on_winning_trades": f"{ avg_profit_winning_trades_rupees } Rs. ({ rounded_avg_profit_winning_trades } Points)",
    #     "average_loss_on_losing_trades": f"{ avg_loss_lossing_trades_rupees } Rs. ({ rounded_avg_loss_lossing_trades } Points)",

    #     "max_daily_profit": f"{ max_t_rupees } Rs. ({ max_t } Points)",
    #     "max_daily_loss": f"{ min_t_rupees } Rs. ({ min_t } Points)",
        
    #     "tradewise_accuracy": f"{tradewise_accuracy}%",
    #     "day_wise_max_drawdown": f"{ day_wise_dd_rupees } Rs. ({ day_wise_dd } Points)",
    #     "tradewise_max_drawdown": f"{ trade_wise_dd_rupees } Rs. ({ trade_wise_dd } Points)",
    #     "winning_streak_daywise": f"{max_win_streak} Days",
    #     "losing_streak_daywise": f"{max_loss_streak} Days",
    #     "returns_max_dd_ratio": f"{returns_dd_ratio}",
    #     "expectancy_trade": f"{expectancy_ratio}",
    #     "expectancy_day": f"{expectancy_ratio1}"

        
    # }
    # daywise = {

    #     "2020" : {
    #         "Mon": f"{rounded_monday_2020}",
    #         "Tues": f"{rounded_tuesday_2020}",
    #         "Wed": f"{rounded_wednesday_2020}",
    #         "Thur": f"{rounded_thursday_2020}",
    #         "Fri": f"{rounded_friday_2020}",
    #     },
    #     "ROI_2020" : {
    #         "Mon": f"{rounded_monday_roi_2020}",
    #         "Tues": f"{rounded_tuesday_roi_2020}",
    #         "Wed": f"{rounded_wednesday_roi_2020}",
    #         "Thur": f"{rounded_thursday_roi_2020}",
    #         "Fri": f"{rounded_friday_roi_2020}"
    #     },

    #     "2021" : {
    #         "Mon": f"{rounded_monday_2021}",
    #         "Tues": f"{rounded_tuesday_2021}",
    #         "Wed": f"{rounded_wednesday_2021}",
    #         "Thur": f"{rounded_thursday_2021}",
    #         "Fri": f"{rounded_friday_2021}",
    #     },
    #     "ROI_2021" : {
    #         "Mon": f"{rounded_monday_roi_2021}",
    #         "Tues": f"{rounded_tuesday_roi_2021}",
    #         "Wed": f"{rounded_wednesday_roi_2021}",
    #         "Thur": f"{rounded_thursday_roi_2021}",
    #         "Fri": f"{rounded_friday_roi_2021}"
    #     },


    #     "2022" : {
    #         "Mon": f"{rounded_monday_2022}",
    #         "Tues": f"{rounded_tuesday_2022}",
    #         "Wed": f"{rounded_wednesday_2022}",
    #         "Thur": f"{rounded_thursday_2022}",
    #         "Fri": f"{rounded_friday_2022}",
    #     },
    #     "ROI_2022" : {
    #         "Mon": f"{rounded_monday_roi_2022}",
    #         "Tues": f"{rounded_tuesday_roi_2022}",
    #         "Wed": f"{rounded_wednesday_roi_2022}",
    #         "Thur": f"{rounded_thursday_roi_2022}",
    #         "Fri": f"{rounded_friday_roi_2022}"
    #     },

    #         "2023" : {
    #         "Mon": f"{rounded_monday_2023}",
    #         "Tues": f"{rounded_tuesday_2023}",
    #         "Wed": f"{rounded_wednesday_2023}",
    #         "Thur": f"{rounded_thursday_2023}",
    #         "Fri": f"{rounded_friday_2023}",
    #     },
    #     "ROI_2023" : {
    #         "Mon": f"{rounded_monday_roi_2023}",
    #         "Tues": f"{rounded_tuesday_roi_2023}",
    #         "Wed": f"{rounded_wednesday_roi_2023}",
    #         "Thur": f"{rounded_thursday_roi_2023}",
    #         "Fri": f"{rounded_friday_roi_2023}"
    #     }  
    # }

    # monthwise = {
    #     "2020" : {
    #         "Jan": f"{rounded_january_2020}",
    #         "Feb": f"{rounded_february_2020}",
    #         "Mar": f"{rounded_march_2020}",
    #         "Apr": f"{rounded_april_2020}",
    #         "May": f"{rounded_may_2020}",
    #         "Jun": f"{rounded_june_2020}",
    #         "Jul": f"{rounded_july_2020}",
    #         "Aug": f"{rounded_august_2020}",
    #         "Sep": f"{rounded_september_2020}",
    #         "Oct": f"{rounded_october_2020}",
    #         "Nov": f"{rounded_november_2020}",
    #         "Dec": f"{rounded_december_2020}"
    #     },
    #     "ROI_2020" : {
    #         "Jan": f"{rounded_january_roi_2020}",
    #         "Feb": f"{rounded_february_roi_2020}",
    #         "Mar": f"{rounded_march_roi_2020}",
    #         "Apr": f"{rounded_april_roi_2020}",
    #         "May": f"{rounded_may_roi_2020}",
    #         "Jun": f"{rounded_june_roi_2020}",
    #         "Jul": f"{rounded_july_roi_2020}",
    #         "Aug": f"{rounded_august_roi_2020}",
    #         "Sep": f"{rounded_september_roi_2020}",
    #         "Oct": f"{rounded_october_roi_2020}",
    #         "Nov": f"{rounded_november_roi_2020}",
    #         "Dec": f"{rounded_december_roi_2020}"
    #     },
    #     "2021" : {
    #         "Jan": f"{rounded_january_2021}",
    #         "Feb": f"{rounded_february_2021}",
    #         "Mar": f"{rounded_march_2021}",
    #         "Apr": f"{rounded_april_2021}",
    #         "May": f"{rounded_may_2021}",
    #         "Jun": f"{rounded_june_2021}",
    #         "Jul": f"{rounded_july_2021}",
    #         "Aug": f"{rounded_august_2021}",
    #         "Sep": f"{rounded_september_2021}",
    #         "Oct": f"{rounded_october_2021}",
    #         "Nov": f"{rounded_november_2021}",
    #         "Dec": f"{rounded_december_2021}"
    #     },
    #     "ROI_2021" : {
    #         "Jan": f"{rounded_january_roi_2021}",
    #         "Feb": f"{rounded_february_roi_2021}",
    #         "Mar": f"{rounded_march_roi_2021}",
    #         "Apr": f"{rounded_april_roi_2021}",
    #         "May": f"{rounded_may_roi_2021}",
    #         "Jun": f"{rounded_june_roi_2021}",
    #         "Jul": f"{rounded_july_roi_2021}",
    #         "Aug": f"{rounded_august_roi_2021}",
    #         "Sep": f"{rounded_september_roi_2021}",
    #         "Oct": f"{rounded_october_roi_2021}",
    #         "Nov": f"{rounded_november_roi_2021}",
    #         "Dec": f"{rounded_december_roi_2021}"
    #     },
    #         "2022" : {
    #         "Jan": f"{rounded_january_2022}",
    #         "Feb": f"{rounded_february_2022}",
    #         "Mar": f"{rounded_march_2022}",
    #         "Apr": f"{rounded_april_2022}",
    #         "May": f"{rounded_may_2022}",
    #         "Jun": f"{rounded_june_2022}",
    #         "Jul": f"{rounded_july_2022}",
    #         "Aug": f"{rounded_august_2022}",
    #         "Sep": f"{rounded_september_2022}",
    #         "Oct": f"{rounded_october_2022}",
    #         "Nov": f"{rounded_november_2022}",
    #         "Dec": f"{rounded_december_2022}"
    #     },
    #     "ROI_2022" : {
    #         "Jan": f"{rounded_january_roi_2022}",
    #         "Feb": f"{rounded_february_roi_2022}",
    #         "Mar": f"{rounded_march_roi_2022}",
    #         "Apr": f"{rounded_april_roi_2022}",
    #         "May": f"{rounded_may_roi_2022}",
    #         "Jun": f"{rounded_june_roi_2022}",
    #         "Jul": f"{rounded_july_roi_2022}",
    #         "Aug": f"{rounded_august_roi_2022}",
    #         "Sep": f"{rounded_september_roi_2022}",
    #         "Oct": f"{rounded_october_roi_2022}",
    #         "Nov": f"{rounded_november_roi_2022}",
    #         "Dec": f"{rounded_december_roi_2022}"
    #     },
    #         "2023" : {
    #         "Jan": f"{rounded_january_2023}",
    #         "Feb": f"{rounded_february_2023}",
    #         "Mar": f"{rounded_march_2023}",
    #         "Apr": f"{rounded_april_2023}",
    #         "May": f"{rounded_may_2023}",
    #         "Jun": f"{rounded_june_2023}",
    #         "Jul": f"{rounded_july_2023}",
    #         "Aug": f"{rounded_august_2023}",
    #         "Sep": f"{rounded_september_2023}",
    #         "Oct": f"{rounded_october_2023}",
    #         "Nov": f"{rounded_november_2023}",
    #         "Dec": f"{rounded_december_2023}"
    #     },
    #     "ROI_2023" : {
    #         "Jan": f"{rounded_january_roi_2023}",
    #         "Feb": f"{rounded_february_roi_2023}",
    #         "Mar": f"{rounded_march_roi_2023}",
    #         "Apr": f"{rounded_april_roi_2023}",
    #         "May": f"{rounded_may_roi_2023}",
    #         "Jun": f"{rounded_june_roi_2023}",
    #         "Jul": f"{rounded_july_roi_2023}",
    #         "Aug": f"{rounded_august_roi_2023}",
    #         "Sep": f"{rounded_september_roi_2023}",
    #         "Oct": f"{rounded_october_roi_2023}",
    #         "Nov": f"{rounded_november_roi_2023}",
    #         "Dec": f"{rounded_december_roi_2023}"
    #     }
    # }

    # # text_file.write(leg)
    # #changehere
    # daywise_object = create_json(daywise)
    # print(daywise_object)

    # monthwise_object = create_json(monthwise)
    # print(monthwise_object)
    # json_object = create_json(summary_report)
    # print(json_object)


    return Response("Backtesting Completed.", status=200)