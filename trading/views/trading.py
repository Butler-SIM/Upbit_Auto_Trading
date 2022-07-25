import json
import requests
from django.http import JsonResponse
from pyupbit import *
from datetime import datetime, timedelta, date

from rest_framework import status, generics
from rest_framework.decorators import api_view
import requests
import upbit
from json_response import json_success, json_error
from config.settings.deploy import *
from slack.views import slack_post_message
from trading.models import TradingHistoryModel
from user.models import UserModel
import pyupbit
import aiohttp, asyncio, re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from asgiref.sync import sync_to_async

sched = BlockingScheduler(timezone='Asia/Seoul')

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


def get_balance(ticker, upbit):
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
    # print("autotrade start")
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


def get_start_price(ticker):
    """
    시가 조회(한국시간 오전 9시)
    """

    try:
        url = f"https://api.upbit.com/v1/candles/days?market={ticker}&count=1"

        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)

        return response.json()[0]["opening_price"]

    except Exception as e :
        print("error ticker : ", ticker)
        print(e)
        return 1.00001


def change_rate(ticker):
    """
    시가 대비 현재가 상승률
    :param ticker:
    :return:
    """
    result = {}
    for key, value in ticker.items():
        result[key] = round(value / get_start_price(key), 3)
        time.sleep(0.06)

    sort_result = (dict(sorted(result.items(), key=lambda x: x[1], reverse=True)))
    return sort_result

@sync_to_async
def _getUserModel(pk, status):
    user_model = UserModel.objects.get(id=1)

    return user_model


def _get_trading_history():
    today = date.today()
    yester_day = today - timedelta(days=1)
    now_time = datetime.now()
    if 9 < now_time.hour < 24:
        # 오전 9~23시59분까지
        start_time = datetime(int(today.year), int(today.month), int(today.day), 9, 0, 0)
        end_time = datetime(int(today.year), int(today.month), int(today.day), 23, 59, 59)
    else:
        # 24 이후는 전날 09시~ 금일 08시59분
        start_time = datetime(int(yester_day.year), int(yester_day.month), int(yester_day.day), 9, 0, 0)
        end_time = datetime(int(today.year), int(today.month), int(today.day), 8, 59, 59)
    #print(f"start_time : {start_time} end_time : {end_time}")
    history = TradingHistoryModel.objects.filter(created_at__range=(start_time, end_time), type='buy')

    return history



async def safe_auto_trading():
    # 로그인
    upbit = pyupbit.Upbit(access, secret)
    krw_all_ticker = get_tickers("KRW")
    print(krw_all_ticker)
    current_price = pyupbit.get_current_price(krw_all_ticker)
    rate = change_rate(current_price)
    print(rate)

    # print("autotrade start")
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


def dangerous_auto_trading():
    # 로그인
    upbit = pyupbit.Upbit(access, secret)
    krw_all_ticker = get_tickers("KRW")
    print(krw_all_ticker)
    current_price = pyupbit.get_current_price(krw_all_ticker)
    rate = change_rate(current_price)
    print(rate)
    user = UserModel.objects.get(nick_name='가가가')
    today_history = _get_trading_history()
    today_buy_coin_list = [i.get('current') for i in today_history.filter(type='buy').values('current')]
    print("today_history", today_history)
    try:
        #전체 계좌 조회
        balance = upbit.get_balances()
        print("balance", balance)
        for_count = 0
        for k, v in rate.items():
            print("k ", k)
            if k in today_buy_coin_list:
                # 오늘 이미 거래한 코인 이면 더이상 거래 하지 않음
                continue
            if today_history.filter(type='buy').count() > 7:
                # 하루 최대 거래 8번까지
                return False
            if 1.014 < rate[k] < 1.072:
                print(f"kkkkk : {k} valut {v}" )
                my_krw = math.trunc(get_balance("KRW", upbit)) - 5000

                buy_coin = k.replace('KRW-', "")
                print("구매 할 코인", buy_coin)
                print("my_krw", my_krw)
                # 현재가 전액 매수 시장가 주문
                coin_price =pyupbit.get_current_price(k)
                coin_buy_count = round((my_krw  / coin_price), 4)
                print('coin_buy_count', coin_buy_count)
                print('coin_price', coin_price)

                upbit.buy_market_order(k, my_krw)
                sell_coin_count = upbit.get_balance_t(k)
                avg_buy_price = upbit.get_avg_buy_price(buy_coin)
                trading = TradingHistoryModel.objects.create(
                    coin=buy_coin, purchase_price=avg_buy_price, count=sell_coin_count, user_id=user, type="buy",
                    current=k, total_price=my_krw
                )
                user.dangerous_coin_possession = True
                user.save()
                # 슬랙 메세지 보내기
                slack_post_message(trading)

                break

            for_count += 1
            if for_count == 5 :
                break

    except Exception as e:
        print(e)
        pass


def sell_coin(status=None):
    upbit = pyupbit.Upbit(access, secret)
    user = UserModel.objects.get(nick_name="가가가")
    my_coin = TradingHistoryModel.objects.filter(type='buy').last()
    current_price = pyupbit.get_current_price(my_coin.current)
    sell_coin_count = upbit.get_balance_t(my_coin.current)
    print(f"current_price = {current_price} my_coin.purchase_price = {my_coin.purchase_price}")
    avg_buy_price = upbit.get_avg_buy_price(my_coin.coin)
    rate = (current_price / avg_buy_price)

    print("avg_buy_price : ", avg_buy_price)
    print("rate : ", rate)
    print("buy_coin : ", my_coin.current)
    print("코인팔기")
    now_time = datetime.now()

    # 시장가 매도
    if rate > 1.051:
        # 내가 산 가격보다 5.2% 이상 상승시 시장가 매도
        print("5.2% 상승 ")
        try:
            sell_coin = upbit.sell_market_order(my_coin.current, sell_coin_count)
            trading = TradingHistoryModel.objects.create(
                coin=my_coin.coin, sale_price=current_price, count=sell_coin_count, user_id=user, type="sell",
                current=my_coin.current, roe=rate
            )
            user.dangerous_coin_possession = False
            user.save()

            slack_post_message(trading, sell_coin)

            return False
        except Exception as e:
            print(e)

    if rate < 0.987:
        print("1.3% 하락 ")
        # 내가 산 가격보다 1.5% 이상 하락시 시장가 매도
        print(f"코인명 {my_coin.current} 코인 갯수 {sell_coin_count}")
        sell_coin = upbit.sell_market_order(my_coin.current, sell_coin_count)

        trading = TradingHistoryModel.objects.create(
            coin=my_coin.coin, sale_price=current_price, count=sell_coin_count, user_id=user, type="sell",
            current=my_coin.current, roe=rate
        )

        user.dangerous_coin_possession = False
        user.save()
        slack_post_message(trading, sell_coin)

        return False
    if now_time > (my_coin.created_at + timedelta(hours=5)):
        print("5시간 경과 ")
        # 매수 후 5시간 넘은 경우 (5.%이상 상승, 1.5%이상 하락이 일어나지 않은경우 현재가 매도)
        sell_coin = upbit.sell_market_order(my_coin.current, sell_coin_count)

        trading = TradingHistoryModel.objects.create(
            coin=my_coin.coin, sale_price=current_price, count=sell_coin_count, user_id=user, type="sell",
            current=my_coin.current, roe=rate
        )

        user.dangerous_coin_possession = False
        user.save()

        slack_post_message(trading, sell_coin)

        return False

    if status == 'time_8':
        print("현재 시간 오전 8시 ")
        # 오전 8시부터 9시 까지 자동 매매 꺼둠 보유 한 코인 있다면 현재가 매도
        sell_coin = upbit.sell_market_order(my_coin.current, sell_coin_count)

        trading = TradingHistoryModel.objects.create(
            coin=my_coin.coin, sale_price=current_price, count=sell_coin_count, user_id=user, type="sell",
            current=my_coin.current, roe=rate
        )

        user.dangerous_coin_possession = False
        user.save()

        slack_post_message(trading, sell_coin)


def secure_transaction_schedule():
    now_time = datetime.now()
    user = UserModel.objects.get(nick_name='가가가')
    print("user.dangerous_coin_possession : ", user.dangerous_coin_possession)
    today_history = _get_trading_history()

    # 오전8시부터 9시까지 거래 하지않음
    if 8 == now_time.hour:
        # 매수 한 코인 있으면 현재가 매도
        if user.dangerous_coin_possession:
            sell_coin("time_8")
            user.dangerous_trading_status = False
            user.save()
        # 매수 한 코인이 없으면
        else:
            # 자동매매 상태 False로 변경
            user.dangerous_trading_status = False
            user.save()
    # 9시가 되면 자동 매매상태 True로 변경
    elif 9 == now_time.hour:
        user.dangerous_trading_status = True
        user.save()

    if not user.dangerous_trading_status:
        print("자동매매 꺼둠")
        return False
    # 위험거래 5번 넘어가면 위험거래 상태 False로변경
    # if today_history.filter(type='buy').count() > 4:
    #     user.dangerous_trading_status = False
    #     user.save()
    #     # 하루 최대 거래 5번까지
    #     return False

    # 포지션 있는 경우
    if user.dangerous_coin_possession:
        print("포지션 있음")
        sell_coin()
    # 포지션 없고 위엄거래 상태가 True인 경우 매수
    elif user.dangerous_trading_status and not user.dangerous_coin_possession:
        dangerous_auto_trading()


schedulers = BackgroundScheduler(misfire_grace_time=3600, coalesce=True)
schedulers.add_job(secure_transaction_schedule, 'interval', seconds=15)
schedulers.start()
