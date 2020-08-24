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
import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from oms.oms_api import *


urlpatterns = [
    url(r'^user_add/$',views.user_add,name="user_add"),
    url(r'^user_edit/$',views.user_edit,name="user_edit"),
    url(r'^user_list/$',views.user_list,name="user_list"),
    url(r'^user_del/$',views.user_del,name="user_del"),
    url(r'^change_pass/$',views.change_pass,name="change_pass"),
    url(r'^forget_pass/$',views.forget_pass,name="forget_pass"),
    url(r'^add_group/$',login_required(views.GroupUser.as_view()),name="add_group"),
]

