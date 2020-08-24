"""oms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from jenkinsapp import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from oms.oms_api import *


urlpatterns = [
    #url(r'^charjs/$',views.charJs,name="charJs"),
    url(r'^data/$',views.jdata,name="jenkinsdata"),
    url(r'^install/$',login_required(views.jinstall),name="jenkinsinstall"),
    url(r'^jbuild_prog/$',login_required(views.build_prog2),name="jbuild_prog"),
    url(r'^console/$',login_required(views.jconsole),name="jenkinsconsole"),
    url(r'^createjob/$',login_required(views.createNewJob),name="jenkinscreatejob"),
    url(r'^get_ip_info/$',login_required(views.get_ip_info),name="getipinfo"),
]

