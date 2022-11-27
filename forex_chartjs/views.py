from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response
import psycopg2
from .serializers import *
from .models import *
from rest_framework import viewsets
import requests
from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pytz
import json 

url = 'https://api.exchangerate.host/latest'
SS_URL = 'https://api.exchangerate.host/latest'
paid_api = "https://marketdata.tradermade.com/api/v1/live"
TradeMade_api_key = "GUW3KKLa9oV8fj3PbXvo"

def get_data_mt5(currency_name):
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        return None
    try:
        utc_from = datetime.now(tz=pytz.utc) - timedelta(minutes=1)
        utc_to = datetime.now(tz=pytz.utc)
        ticks = mt5.copy_ticks_range(currency_name, utc_from, utc_to, mt5.COPY_TICKS_ALL)
        ticks_frame = pd.DataFrame(ticks)
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
        ticks_frame = ticks_frame.set_index(ticks_frame['time'])
        data_ask = ticks_frame['ask'].resample("1s").ohlc()
        data_bid = ticks_frame['bid'].resample("1s").ohlc()
        data = pd.DataFrame()
        data['open'] = (data_ask['open'] + data_bid['open']) / 2
        data['high'] = (data_ask['high'] + data_bid['high']) / 2
        data['low'] = (data_ask['low'] + data_bid['low']) / 2
        data['close'] = (data_ask['close'] + data_bid['close']) / 2
        data = data.reset_index()
        data = data.fillna(data.mean(numeric_only=True))
        current_value = ((ticks_frame['ask'] + ticks_frame['bid']) / 2)
        current_price = current_value.tail(1).values[-1]
        current_price = round(current_price, 5)

        return current_price
    except Exception as e:
        print("[ERROR]", e)
        return None

def free_api(currency_name):
    response = requests.get(SS_URL)
    data = response.json()
    currency_1 = currency_name[:3]
    currency_2 = currency_name[3:]
    current_price = data['rates'][currency_2] / data['rates'][currency_1]
    current_price = round(current_price, 5)
    return current_price

def TradeMade(currency_name):
    querystring = {"currency":currency_name,"api_key":TradeMade_api_key}
    response = requests.get(paid_api, params=querystring)
    data = response.json()
    ask_price = data['quotes'][0]['ask']
    bid_price = data['quotes'][0]['bid']
    current_price = (ask_price + bid_price)/2
    current_price = round(current_price, 5)
    return current_price

def get_data(request):
    mydb = psycopg2.connect(
        database="postgres", user='postgres', password='admin', host='127.0.0.1', port='5432')

    currency__ = ""
    interval__ = ""
    method_ = "1"

    if request.GET.get('currency'):
        currency__ = request.GET.get('currency')

    if request.GET.get('interval'):
        interval__ = request.GET.get('interval')
        interval__ = interval__ + "Min"

    if request.GET.get('method_'):
        method_ = request.GET.get('method_')

    currency = "AUDUSD"
    time_interval = "15Min"
    mydb.autocommit = True
    cursor = mydb.cursor()

    if currency__ == '':
        sql_current_price = "SELECT current_price from currency_buy_sell where currency = '" + currency + "' "
    else:
        sql_current_price = "SELECT current_price from currency_buy_sell where currency = '" + currency__ + "' "
    cursor.execute(sql_current_price)   
    result_current_price = cursor.fetchall()[0][0]

    if currency__ == '':
        sql_query_buy = "SELECT buy from currency_buy_sell where currency = '" + currency + "' "
    else:
        sql_query_buy = "SELECT buy from currency_buy_sell where currency = '" + currency__ + "' "
    cursor.execute(sql_query_buy)
    result_buy = cursor.fetchall()[0][0]

    if currency__ == '':
        sql_query_sell = "SELECT sell from currency_buy_sell where currency = '" + currency + "' "
    else:
        sql_query_sell = "SELECT sell from currency_buy_sell where currency = '" + currency__ + "' "
    cursor.execute(sql_query_sell)
    result_sell = cursor.fetchall()[0][0]

    if currency__ == '':
        sql_query_predicted_high_low = "Select currency, time_interval, high, high_prediction, date_time_hit_high, low, low_prediction, date_time_hit_low FROM predicted_high_low_vw where currency = '" + currency + "'"
    else:
        sql_query_predicted_high_low = "Select currency, time_interval, high, high_prediction, date_time_hit_high, low, low_prediction, date_time_hit_low FROM predicted_high_low_vw where currency = '" + currency__ + "'"

    cursor.execute(sql_query_predicted_high_low)
    result_high_low = cursor.fetchall()

    if currency__ != '' and interval__ == '':
        sql_query_historical_data = "SELECT current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, target_datetime, datetime_hit_high, datetime_hit_low from historical_data where currency = '" + currency__ + "' order by current_time_ desc"
    elif currency__ != '' and interval__ != '':
        sql_query_historical_data = "SELECT current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, target_datetime, datetime_hit_high, datetime_hit_low from historical_data where currency = '" + currency__ + "' and time_interval = '" + interval__ + "'order by current_time_ desc"
    else:
        sql_query_historical_data = "SELECT current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, target_datetime, datetime_hit_high, datetime_hit_low from historical_data order by current_time_ desc"

    cursor.execute(sql_query_historical_data)
    result_historical = cursor.fetchall()

    currency_ = Currency.objects.all()
    time_interval = Interval.objects.all()

    context = {
        "Buy": result_buy,
        "Sell": result_sell,
        "high_low": result_high_low,
        "historical_data": result_historical,
        "Get_currency": currency_,
        "Get_interval": time_interval,
        "currency": currency__,
        "current_price": result_current_price,
    }

    return render(request, 'chartjs/demo_v1.html', context)
    # return render(request, context, template_name)

def get_currency(request):
    mydb = psycopg2.connect(
        database="postgres", user='postgres', password='admin', host='127.0.0.1', port='5432')

    mydb.autocommit = True
    cursor = mydb.cursor()

    currency = "AUDUSD"
    currency__ = ""
    interval__ = ""

    if request.GET.get('currency'):
        currency__ = request.GET.get('currency')

    if request.GET.get('interval'):
        interval__ = request.GET.get('interval')
        interval__ = interval__ + "Min"

    if request.GET.get('method_'):
        method_ = request.GET.get('method_')

    if currency__ == '':
        if int(method_)== 0:
            current_price = get_data_mt5(currency__)
 
        elif int(method_) == 1:
            current_price = free_api(currency__)

        elif int(method_) == 2:
            current_price = TradeMade(currency__)
        sql_current_price = "SELECT current_price from currency_buy_sell where currency = '" + currency + "' "
    else:
        if int(method_)== 0:
            current_price = get_data_mt5(currency__)
 
        elif int(method_) == 1:
            current_price = free_api(currency__)

        elif int(method_) == 2:
            current_price = TradeMade(currency__)

        sql_current_price = "SELECT current_price from currency_buy_sell where currency = '" + currency__ + "' "
    cursor.execute(sql_current_price)
    result_current_price = cursor.fetchall()[0][0]
    cursor = None
    cursor = mydb.cursor()

    if currency__ == '':
        sql_query_buy = "SELECT buy from currency_buy_sell where currency = '" + currency + "' "
    else:
        sql_query_buy = "SELECT buy from currency_buy_sell where currency = '" + currency__ + "' "
    cursor.execute(sql_query_buy)
    result_buy = cursor.fetchall()[0][0]

    if currency__ == '':
        sql_query_sell = "SELECT sell from currency_buy_sell where currency = '" + currency + "' "
    else:
        sql_query_sell = "SELECT sell from currency_buy_sell where currency = '" + currency__ + "' "
    cursor.execute(sql_query_sell)
    result_sell = cursor.fetchall()[0][0]

    if currency__ == '':
        sql_query_high_low = "Select currency, time_interval, high, high_prediction, date_time_hit_high, low, low_prediction, date_time_hit_low FROM predicted_high_low_vw order by time_interval_id asc"
    else:
        sql_query_high_low = "Select currency, time_interval, high, high_prediction, date_time_hit_high, low, low_prediction, date_time_hit_low FROM predicted_high_low_vw where currency = '" + currency__ + "' order by time_interval_id asc "
    cursor.execute(sql_query_high_low)
    result_high_low = cursor.fetchall()


    if currency__ != '' and interval__ == '':
        sql_query_historical_data = "SELECT current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, target_datetime, datetime_hit_high, datetime_hit_low from historical_data where currency = '" + currency__ + "' order by current_time_ desc"
    elif currency__ != '' and interval__ != '':
        sql_query_historical_data = "SELECT current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, target_datetime, datetime_hit_high, datetime_hit_low from historical_data where currency = '" + currency__ + "' and time_interval = '" + interval__ + "' order by current_time_ desc"
    else:
        sql_query_historical_data = "SELECT current_time_, currency, time_interval, round(actual_high::numeric, 5) as actual_high, round(actual_low::numeric, 5) as actual_low, round(predicted_high::numeric, 5) as predicted_high, round(predicted_low::numeric, 5) as predicted_low, target_datetime, datetime_hit_high, datetime_hit_low from historical_data order by current_time_ desc"

    cursor.execute(sql_query_historical_data)
    result_historical = cursor.fetchall()

    response = {
    'method' : method_,
    'current_price': current_price,
    'result_buy': str(result_buy),
    'result_sell': str(result_sell),
    'result_high_low': result_high_low,
    'result_historical': result_historical
    }

    return JsonResponse(response)


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class IntervalViewSet(viewsets.ModelViewSet):
    queryset = Interval.objects.all()
    serializer_class = IntervalSerializer
