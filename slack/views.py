from django.shortcuts import render

# Create your views here.

import slack_sdk

from config.settings.deploy import slack_bot_key

client = slack_sdk.WebClient(token=slack_bot_key)


def slack_post_message(trading_history):
    print(trading_history)
    if trading_history.type == "buy":
        text = f"코인 매수 \n코인명 : {trading_history.coin} \n평균 매수가 : {trading_history.purchase_price} \n 코인 개수 : {trading_history.count} \n 총 가격 : {trading_history.total_price} "
    else:
        text = f"코인 매도 \n코인명 : {trading_history.coin} \n매도가 : {trading_history.purchase_price} \n 코인 개수 : {trading_history.count} \n 총 가격 : {trading_history.total_price} \n ROE : {trading_history.roe}"
    client.chat_postMessage(channel='history', text=text)
