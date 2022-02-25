from django.contrib import admin

# Register your models here.
from mainapp.models import MainappModel, ProjectImageModel, ProjectInfoModel


@admin.register(MainappModel)
class MainappAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'main_intro',
    )

    list_display_links = (
        'id',
        'main_intro',
    )

    search_fields = [
        'id',
        'main_intro',
    ]

@admin.register(ProjectInfoModel)
class ProjectInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'project_name',
        'category',
    )
    list_display_links = (
        'id',
        'project_name',
        'category',
    )

    search_fields = [
        'id',
        'project_name',
        'category',
    ]


@admin.register(ProjectImageModel)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'project_image',
        'project_id',
    )
    list_display_links = (
        'id',
        'project_image',
        'project_id',
    )

    search_fields = [
        'id',
        'project_image',
        'project_id',
    ]
