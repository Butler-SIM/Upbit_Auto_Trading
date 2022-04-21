import json

import bcrypt
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from rest_framework import status, generics
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Parameter, IN_HEADER, TYPE_STRING
import upbit
from json_response import json_success, json_error
from config.settings.deploy import *
from user.models import UserModel
from user.serializer import UserModelSerializer
import time
import pyupbit
import datetime
from config import *


class MyPageView(generics.ListCreateAPIView):
    """
    마이 페이지
    ---
     [GET] : 마이 페이지 조회
    """

    def get(self, request, *args, **kwargs):
        """
        마이 페이지
        ---
         [GET] : 마이 페이지 조회
        """
        if UserModel.objects.get(kakao_key=request.session['kakao_id']):

            user_model = UserModel.objects.get(kakao_key=request.session['kakao_id'])
            model = {'safe_trading_status': user_model.safe_trading_status}

            return render(request, 'my_page.html', model)

        else:
            return render(request, 'login.html')


@api_view(["PUT"])
def trading_switch(request):
    """
    자동 매매 설정
    /user/trading_switch
    """
    try:
        user_model = UserModel.objects.filter(kakao_key=request.session['kakao_id'])
        if request.data['status'] == '0':
            user_model.update(safe_trading_status='1')

            return JsonResponse(json_success("S0004", {"CODE": "success1001"}), status=status.HTTP_200_OK)
        else:

            user_model.update(safe_trading_status='0')
            return JsonResponse(json_success("S0004", {"CODE": "success1002"}), status=status.HTTP_200_OK)

    except Exception:
        return JsonResponse(json_success("S0004", {"CODE": "error4001"}), status=status.HTTP_200_OK)

