#from cryptography.fernet import Fernet
from django.shortcuts import render
import pyupbit
# Create your views here.
from server_settings.settings.deploy import *


from user.models import UserModel


def get_test():


    return {"dec_access_key" : "dec_access_key", "dec_secret_key": "1111"}

def upbit(request):
    user_model = UserModel.objects.get(id = 1)
    tickers = pyupbit.get_tickers(fiat="KRW")

    #encode_upbit_key = rsa.encrypt(access_key.encode(),pubkey)

    #entxt = encrypt('123132','random')
    #user_model.upbit_access_key = entxt
    #user_model.save()

    #decText = decrypt(user_model.upbit_access_key,randomTxt)
    #print(decText)
    #dec_upbit_key = rsa.decrypt(encode_upbit_key, private).decode()

    #print(dec_upbit_key)

    str1 = "I am okay"
    #key = Fernet.generate_key()
    #print("key : ", key)
    #upbit = pyupbit.Upbit(access_key, secret_key)

    return render(request, 'upbittest.html')