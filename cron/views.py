from datetime import datetime

from trading.views.trading import *
from asgiref.sync import sync_to_async

sched = BlockingScheduler(timezone='Asia/Seoul')


@sync_to_async
def save_result(pk, status):
   pass


async def auto_trading():
    # 로그인
    upbit = pyupbit.Upbit(access, secret)
    #print("autotrade start")
    user_model = UserModel.objects.get(id=1)

    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw * 0.9995)

        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc * 0.9995)
    except Exception as e:
        print(e)
        pass




def secure_transaction_schedule():
    #print("schedule!!!!!!!")
    asyncio.run(auto_trading())


schedulers = BackgroundScheduler(misfire_grace_time=3600, coalesce=True)
schedulers.start()