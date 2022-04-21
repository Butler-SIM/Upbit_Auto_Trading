from django.urls import path

from .views import *
from .views import my_page, login

app_name = 'user'

urlpatterns = [
    # login.py
    path('', login.user, name='user'),
    path('login', login.LoginView.as_view(), name='login'),
    path('logout', login.logout, name='logout'),
    path('join', login.JoinView.as_view(), name='join'),
    path('kakaoLogin', login.KakaoSignInView.as_view(), name='KakaoSignInView'),
    path('accounts/signin/kakao/callback', login.KaKaoSignInCallBackView.as_view(), name='KaKaoSignInCallBackView'),

    # my_page.py
    path('my_page', my_page.MyPageView.as_view(), name='my_page'),
    path('trading_switch', my_page.trading_switch, name='trading_switch'),

]
