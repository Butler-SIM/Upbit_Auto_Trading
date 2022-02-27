from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status, generics
from rest_framework.decorators import api_view

from json_response import json_success, json_error
from server_settings.settings.deploy import *
from user.models import UserModel
from user.serializer import UserModelSerializer


def user(request):

    return render(request, 'index.html')


class Login(generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):

        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        #en_kakao_key = encrypt(request.data['kakao'], randomTxt)
        #request.data.update(kakao_key=en_kakao_key)

        print(request.data)
        return JsonResponse(json_success("S0004", {"CODE": "succes1111"}), status=status.HTTP_200_OK)

def join(request):

    return render(request, 'join.html')

class Join(generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):

        return render(request, 'join.html')
    """ 회원가입 /user/join """
    def post(self, request, *args, **kwargs):
        en_kakao_key = encrypt(request.data['kakao'],randomTxt)

        request.data.update(kakao_key = str(en_kakao_key)[1:])

        serializer = UserModelSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(raise_exception=True)
            return JsonResponse(json_success("S0004", {"CODE":"succes1111"}), status=status.HTTP_200_OK)
        else:
            return JsonResponse(json_error("E0003"), status=status.HTTP_200_OK)