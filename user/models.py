from django.db import models

# Create your models here.

class UserModel(models.Model):
    class Meta:
        verbose_name        = "유저 정보"
        db_table            = 'user'
    nick_name = models.CharField(max_length=8, unique=True, verbose_name="닉네임")
    kakao_key = models.TextField(verbose_name="카카오 키")
    upbit_access_key = models.TextField(verbose_name="카카오 키")
    upbit_secret_key = models.TextField(verbose_name="카카오 키")
    user_staus = models.CharField(max_length=3, default='1', verbose_name='유저 상태')
    #유저상태
    #1 : 정상, 0 : 정지, 2~9 : 등급, 77 : 탈퇴
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="생성 날짜")
