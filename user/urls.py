
from django.contrib import admin
from django.urls import path

import mainapp
from user.views import *

app_name = 'user'

urlpatterns = [
    path('', user, name='user'),
    path('login', LoginView.as_view(), name='login'),
    path('join', JoinView.as_view(), name='join'),
    path('kakakLogin', KakaoSignInView.as_view(), name='KakaoSignInView'),
    path('accounts/signin/kakao/callback', KaKaoSignInCallBackView.as_view(), name='KaKaoSignInCallBackView'),

]
