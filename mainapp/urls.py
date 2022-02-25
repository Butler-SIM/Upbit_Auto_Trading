
from django.contrib import admin
from django.urls import path

import mainapp
from mainapp.views import *

app_name = 'mainapp'

urlpatterns = [
    path('', main, name='main'),
    path('mainapp/about', about, name='about'),
    path('mainapp/contact', contact, name='contact'),
    path('mainapp/portfolio', portfolio, name='portfolio'),
    path('mainapp/portfolio_details/', portfolio_details, name='portfolio_details'),
    path('mainapp/resume', resume, name='resume'),
    path('mainapp/services', services, name='services'),
]
