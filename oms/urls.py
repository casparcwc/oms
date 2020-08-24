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
from django.conf.urls import include,url
from django.contrib import admin
from oms import views
from zabbix import views as zviews
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from oms_api import *


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',login_required(zviews.zabbixTiggerApi)),
    url(r'^oms/$',views.oms,name="oms"),
    #url(r'^dashboard/$',login_required(zviews.zabbixTiggerApi),name="zabbixDashboard"),
    url(r'^oms/index3/$',views.oms_index3,name="oms_index3"),
    url(r'^login/$',views.login,name="login"),
    #url(r'^login/$','django.contrib.auth.views.login', {'template_name': 'templates/login.html'}),
    url(r'^logout/$',views.logout_view,name="logout"),
    url(r'^zabbix/',include('zabbix.urls')),
    url(r'^omsapp/',include('omsapp.urls')),
    url(r'^jenkins/',include('jenkinsapp.urls')),
    url(r'^redis/',include('redisapp.urls')),
]

handler403 = permission_denied
handler404 = page_not_found
handler500 = page_error
