from django.shortcuts import render

# Create your views here.
def user(request):

    return render(request, 'index.html')

def login(request):

    return render(request, 'login.html')

def join(request):

    return render(request, 'join.html')