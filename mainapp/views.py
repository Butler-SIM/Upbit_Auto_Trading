import os

from django.shortcuts import render

# Create your views here.
from mainapp.models import *


def main(request):

    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def portfolio(request):
    web_list = ''
    app_list = ''
    try:
        if ProjectInfoModel.objects.filter(category = 'web' ).exists():
            web_list = ProjectInfoModel.objects.filter(category = 'web')

        if ProjectInfoModel.objects.filter(category='app').exists():
            app_list = ProjectInfoModel.objects.filter(category = 'app')

    except Exception:
        pass
    model = {"web_list" : web_list, "app_list" : app_list}

    return render(request, 'portfolio.html',model)

def portfolio_details(request):
    id = int(request.GET['id'])

    category = ''

    project_model = ProjectInfoModel.objects.get(id = id)

    if project_model.category == 'web' :
        category = 'Web Developer'
    elif project_model.category == 'app' :
        category = 'BackEnd Developer, Server Developer, Web Developer'

    images_list = ProjectImageModel.objects.filter(project_id = id)

    model = {   'project_name' : project_model.project_name,
                'category' : category,
                'client' : project_model.client,
                'project_period' : project_model.project_period,
                'project_URL' : project_model.project_URL,
                'project_introduction' : project_model.project_introduction,
                "images_list" : images_list
            }

    return render(request, 'portfolio-details.html',model)

def resume(request):
    return render(request, 'resume.html')

def services(request):
    return render(request, 'services.html')

