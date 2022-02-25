from django.db import models

# Create your models here.

class MainappModel(models.Model):
    main_intro = models.CharField(max_length=255, null=True, blank=True, verbose_name="메인 소개글")
    project_id = models.IntegerField(null=False, blank=False, verbose_name="프로젝트 index")

class ProjectImageModel(models.Model):
    project_image = models.ImageField(null=True, blank=True, verbose_name="프로젝트 이미지")
    project_id = models.IntegerField(null=False, blank=False, verbose_name="프로젝트 index")

class ProjectInfoModel(models.Model):
    project_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="프로젝트 name")
    category = models.CharField(max_length=100, null=True, blank=True, verbose_name="프로젝트 정보 Category")
    client = models.CharField(max_length=100, null=True, blank=True, verbose_name="프로젝트 정보 client")
    project_period = models.CharField(max_length=100, null=True, blank=True, verbose_name="프로젝트 정보 project_period")
    project_URL = models.CharField(max_length=100, null=True, blank=True, verbose_name="프로젝트 정보 Project_URL")
    project_introduction = models.TextField(null=True, blank=True, verbose_name="프로젝트 소개")
    project_main_image = models.ImageField(null=True, blank=True, verbose_name="프로젝트 대표 이미지")
