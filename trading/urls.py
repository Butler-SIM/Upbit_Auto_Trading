from django.contrib import admin
from django.urls import path

import mainapp
from trading.views import trading_switch
from user.views import *

app_name = 'trading'

urlpatterns = [
    path('trading_switch', trading_switch, name='trading_switch'),

]
