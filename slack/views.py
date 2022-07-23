from django.shortcuts import render

# Create your views here.

import slack_sdk

from config.settings.deploy import slack_bot_key

client = slack_sdk.WebClient(token=slack_bot_key)


def slack_post_message(**dic):
    client.chat_postMessage(channel='history', text="hihihihi")
