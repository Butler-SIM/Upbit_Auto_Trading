import json

import bcrypt
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from rest_framework import status, generics
from rest_framework.decorators import api_view

import upbit
from json_response import json_success, json_error
from config.settings.deploy import *
from upbit.tradingTest import auto_trading
from user.models import UserModel
from user.serializer import UserModelSerializer
import time
import pyupbit
import datetime


def user(request):
    return render(request, 'index.html')


"""
로그인
/user/Login
"""


class LoginView(generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        # en_kakao_key = encrypt(request.data['kakao'], randomTxt)
        # request.data.update(kakao_key=en_kakao_key)

        return JsonResponse(json_success("S0004", {"CODE": "succes1111"}), status=status.HTTP_200_OK)


"""
회원가입
/user/join
"""


class JoinView(generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):

        return render(request, 'join.html')

    """ 회원가입 /user/join """

    def post(self, request, *args, **kwargs):

        serializer = UserModelSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            request.session['kakao_id'] = request.data['kakao_key']
            return JsonResponse(json_success("S0004", {"CODE": "succes0001"}), status=status.HTTP_200_OK)
        else:
            return JsonResponse(json_error("E0003"), status=status.HTTP_200_OK)


"""
카카오 로그인
/user/kakaoLogin
"""


class KakaoSignInView(generics.ListCreateAPIView):
    def get(self, request):
        app_key = kakao_api_key
        redirect_uri = 'http://localhost:8000/user/accounts/signin/kakao/callback'
        kakao_auth_api = 'https://kauth.kakao.com/oauth/authorize?response_type=code'

        return redirect(
            f'{kakao_auth_api}&client_id={app_key}&redirect_uri={redirect_uri}'
        )


class KaKaoSignInCallBackView(generics.ListCreateAPIView):
    def get(self, request):
        auth_code = request.GET.get('code')
        kakao_token_api = 'https://kauth.kakao.com/oauth/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': kakao_api_key,
            'redirection_uri': 'http://localhost:8000/user/accounts/signin/kakao/callback',
            'code': auth_code
        }

        token_response = requests.post(kakao_token_api, data=data)

        access_token = token_response.json().get('access_token')

        user_info_response = requests.get('https://kapi.kakao.com/v2/user/me',
                                          headers={"Authorization": f'Bearer ${access_token}'})

        user_info_json = user_info_response.json()

        # """암호화"""
        # enc_kakao_key = bcrypt.hashpw(request.session['kakao_id'].encode('utf-8'), bcrypt.gensalt())
        # #회원인 경우 로그인 처리
        # if UserModel.objects.filter(kakao_key = enc_kakao_key).exists():
        #     request.session['kakao_id'] = enc_kakao_key
        #     return redirect(reverse("mainapp:main"))
        # #회원이 아닌 경우 회원가입 페이지로 넘김
        # else:
        #     request.session['enc_kakao_id'] = enc_kakao_key
        #     print(request.session['enc_kakao_id'])
        #     return redirect(reverse("user:join"))

        kakao_key = user_info_json['id']
        # 회원인 경우 로그인 처리
        if UserModel.objects.filter(kakao_key=kakao_key).exists():
            request.session['kakao_id'] = kakao_key
            request.session['nick_name'] = UserModel.objects.get(kakao_key=kakao_key).nick_name
            return redirect(reverse("mainapp:main"))
        # 회원이 아닌 경우 회원가입 페이지로 넘김
        else:
            request.session['enc_kakao_id'] = kakao_key
            return redirect(reverse("user:join"))

        return redirect(reverse("mainapp:main"))


"""
마이 페이지
/user/my_page
"""


class MyPageView(generics.ListCreateAPIView):
    def get(self, request, *args, **kwargs):
        try:
            user_model = UserModel.objects.get(kakao_key=request.session['kakao_id'])
            model = {'auto_trading_status': user_model.auto_trading_status}
            test_Crawler()
            return render(request, 'my_page.html', model)

        except user_model.DoesNotExist:
            return render(request, 'login.html')
        except Exception:
            return render(request, 'login.html')


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

    print("0")
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
                    print("1")

        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc * 0.9995)
                print("2")

        time.sleep(1)
    except Exception as e:
        print(e)
        print("3")
        time.sleep(1)


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
