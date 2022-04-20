import json
import requests
from django.http import JsonResponse

from rest_framework import status, generics
from rest_framework.decorators import api_view

import upbit
from json_response import json_success, json_error
from config.settings.deploy import *
from user.models import UserModel
import pyupbit
import datetime
import aiohttp, asyncio, re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from asgiref.sync import sync_to_async

sched = BlockingScheduler(timezone='Asia/Seoul')
"""
자동매매 설정
/user/trading_switch
"""


@api_view(["PUT"])
def trading_switch(request):
    try:
        user_model = UserModel.objects.filter(kakao_key=request.session['kakao_id'])
        if request.data['status'] == '0':
            user_model.update(auto_trading_status='1')

            return JsonResponse(json_success("S0004", {"CODE": "succes1001"}), status=status.HTTP_200_OK)
        else:

            user_model.update(auto_trading_status='0')
            return JsonResponse(json_success("S0004", {"CODE": "succes1002"}), status=status.HTTP_200_OK)


    except Exception:
        return JsonResponse(json_success("S0004", {"CODE": "error4001"}), status=status.HTTP_200_OK)


"""
자동매매 로직
"""

access = upbit_access_key
secret = upbit_secret_key


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15


def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


def auto_trading():
    # 로그인
    upbit = pyupbit.Upbit(access, secret)
    print("autotrade start")
    user_model = UserModel.objects.get(id=1)

    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw * 0.9995)

        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc * 0.9995)
    except Exception as e:
        print(e)
        pass


def do_crawl():
    url = "https://api.upbit.com/v1/market/all"

    querystring = {"isDetails": "false"}

    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, params=querystring).json()

    # print(response)
    result = {}
    for item in response:
        coin_data = item
        # print(coin_data)
        coin_korean = coin_data['korean_name']
        coin_symbol = coin_data['market'][coin_data['market'].find('-') + 1:]
        # print(coin_symbol)
        result[coin_symbol] = coin_korean
        # result.append({ 'coinKorean': coin_korean, 'coinSymbol': coin_symbol })
    print("upbit do_crawl 완료")
    print("result : ", result)
    return result


def test_Crawler():


    custom_header = {
        'referer': 'http://http://finance.daum.net/quotes/A048410#home',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}

    # 해당 접속 사이트가 아닌 원본데이터가 오는 url 추적. network에서 가지고 온다.
    url = "http://finance.daum.net/api/search/ranks?limit=10"

    req = requests.get(url, headers=custom_header)  # custom_header를 사용하지 않으면 접근 불가

    if req.status_code == requests.codes.ok:
        print("접속 성공")
        stock_data = json.loads(req.text)  # json에 반환된 데이터가 들어가 있다.
        for rank in stock_data['data']:  # stock_data는 'data' key값에 모든 정보가 들어가 있다.
            print(rank['rank'], rank['symbolCode'], rank['name'], rank['tradePrice'])

    else:
        print("Error code")


@sync_to_async
def _getUserModel(pk, status):
   user_model = UserModel.objects.get(id=1)

   return user_model


async def safe_auto_trading():
    # 로그인
    upbit = pyupbit.Upbit(access, secret)
    print("autotrade start")
    user_model = _getUserModel
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw * 0.9995)

        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc * 0.9995)
    except Exception as e:
        print(e)
        pass


async def dangerous_auto_trading():
    # 로그인
    upbit = pyupbit.Upbit(access, secret)
    print("dangerous start")
    user_model = _getUserModel
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw * 0.9995)

        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc * 0.9995)
    except Exception as e:
        print(e)
        pass


def secure_transaction_schedule():
    asyncio.run(safe_auto_trading())


schedulers = BackgroundScheduler(misfire_grace_time=3600, coalesce=True)
schedulers.add_job(secure_transaction_schedule, 'interval', seconds=2.5)
schedulers.start()