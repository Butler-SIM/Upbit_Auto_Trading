
from django.contrib import admin
from django.urls import path

import mainapp
from user.views import *

app_name = 'user'

urlpatterns = [
    path('', user, name='user'),
    path('login', Login.as_view(), name='login'),
    path('join', Join.as_view(), name='join'),

]
