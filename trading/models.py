from django.db import models

# Create your models here.
from user.models import UserModel


class TradingHistoryModel(models.Model):
    coin = models.CharField(max_length=30, default='', verbose_name='코인명')
    purchase_price = models.FloatField(verbose_name='매수가', null=True)
    sale_price = models.FloatField(null=True, verbose_name='매도가')
    roe = models.FloatField(null=True, verbose_name='수익률')  # roe : return on equity
    user_id = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, verbose_name='UserIndex')
    type = models.CharField(max_length=20, null=True)   # 타입 (buy, sell)
    count = models.FloatField(default=0) # 코인 개수
    total_price = models.IntegerField(null=True)
    current = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="생성 날짜")

    class Meta:
        verbose_name = "거래 내역"
        db_table = 'trading_history'