from django.db import models


# Create your models here.

class UserModel(models.Model):
    nick_name = models.CharField(max_length=16, unique=True, verbose_name="닉네임")
    kakao_key = models.TextField(default='', verbose_name="카카오 키")
    upbit_access_key = models.TextField(default='', verbose_name="업비트 엑세스 키")
    upbit_secret_key = models.TextField(default='', verbose_name="업비트 시크릿 키")
    email = models.EmailField(null=True, blank=True, verbose_name='이메일')
    # 유저 상태 - 1 : 정상, 0 : 정지, 2~9 : 등급, 77 : 탈퇴
    user_status = models.CharField(max_length=3, default='1', verbose_name='유저 상태')
    safe_trading_status = models.CharField(max_length=3, default='0', verbose_name='안전 매매 활성화 상태')
    dangerous_coin_possession = models.BooleanField(default=False)
    dangerous_trading_status = models.CharField(max_length=3, default='0', verbose_name='위험 매매 활성화 상태')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="생성 날짜")


    class Meta:
        verbose_name = "유저 정보"
        db_table = 'user'



