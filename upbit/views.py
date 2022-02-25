from django.shortcuts import render
import pyupbit
# Create your views here.
from server_settings.settings.deploy import pubkey, private
import rsa


def upbit(request):
    tickers = pyupbit.get_tickers(fiat="KRW")



    #encode_upbit_key = rsa.encrypt(access_key.encode(),pubkey)

    #print(encode_upbit_key)

    #dec_upbit_key = rsa.decrypt(encode_upbit_key, private).decode()

    #print(dec_upbit_key)



    #upbit = pyupbit.Upbit(access_key, secret_key)

    return render(request, 'upbittest.html')