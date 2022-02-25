
from django.contrib import admin
from django.urls import path

import mainapp
from user.views import *

app_name = 'user2'

urlpatterns = [
    path('', user, name='user'),
    path('login', login, name='login'),
    path('join', join, name='join'),

]
