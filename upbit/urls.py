
from django.contrib import admin
from django.urls import path

import mainapp
from upbit.views import *

app_name = 'upbit'

urlpatterns = [
    path('', upbit, name='upbit'),

]
