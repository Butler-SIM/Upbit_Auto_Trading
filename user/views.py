import bcrypt
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from rest_framework import status, generics
from rest_framework.decorators import api_view

from json_response import json_success, json_error
from server_settings.settings.deploy import *
from upbit.tradingTest import auto_trading
from user.models import UserModel
from user.serializer import UserModelSerializer


def user(request):
    return render(request, 'index.html')


class LoginView(generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        # en_kakao_key = encrypt(request.data['kakao'], randomTxt)
        # request.data.update(kakao_key=en_kakao_key)

        return JsonResponse(json_success("S0004", {"CODE": "succes1111"}), status=status.HTTP_200_OK)


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
            print(request.session['enc_kakao_id'])
            return redirect(reverse("user:join"))

        return redirect(reverse("mainapp:main"))


class MyPageView(generics.ListCreateAPIView):
    def get(self, request, *args, **kwargs):
        try:
            user_model = UserModel.objects.get(kakao_key=request.session['kakao_id'])
            model = {'auto_trading_status': user_model.auto_trading_status}

            return render(request, 'my_page.html', model)

        except user_model.DoesNotExist:
            return render(request, 'login.html')
        except Exception:
            return render(request, 'login.html')

    # def put(self, request, *args, **kwargs):
    #     print(request.data)
    #     if request.data['status'] == '0' :
    #         request.data.update(auto_trading_status = 1)
    #     else:
    #         request.data.update(auto_trading_status = 0)
    #     return JsonResponse(json_success("S0004", {"CODE": "succes0001"}), status=status.HTTP_200_OK)


@api_view(["PUT"])
def trading_switch(request):
    try :
        user_model = UserModel.objects.filter(kakao_key=request.session['kakao_id'])
        if request.data['status'] == '0':
            user_model.update(auto_trading_status = '1')
            return JsonResponse(json_success("S0004", {"CODE": "succes1001"}), status=status.HTTP_200_OK)
        else:
            user_model.update(auto_trading_status = '0')
            return JsonResponse(json_success("S0004", {"CODE": "succes1002"}), status=status.HTTP_200_OK)


    except Exception:
        pass