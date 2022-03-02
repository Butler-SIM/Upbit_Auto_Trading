import os

from django.shortcuts import render

# Create your views here.
from mainapp.models import *

"""
메인
/
"""
def main(request):

    return render(request, 'index.html')




