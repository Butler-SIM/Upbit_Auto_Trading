from django.contrib import admin
from django.urls import path

import mainapp
from user.views import *

app_name = 'user'

urlpatterns = [
    path('', user, name='user'),
    path('login', LoginView.as_view(), name='login'),
    path('join', JoinView.as_view(), name='join'),
    path('kakaoLogin', KakaoSignInView.as_view(), name='KakaoSignInView'),
    path('accounts/signin/kakao/callback', KaKaoSignInCallBackView.as_view(), name='KaKaoSignInCallBackView'),
    path('my_page', MyPageView.as_view(), name='my_page'),
    path('trading_switch', trading_switch, name='trading_switch'),

]
