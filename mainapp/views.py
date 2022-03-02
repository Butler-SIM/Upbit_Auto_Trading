import os

from django.shortcuts import render

# Create your views here.
from mainapp.models import *


def main(request):

    return render(request, 'index.html')




