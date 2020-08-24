#-*- coding: utf-8 -*-
from django.shortcuts import render,redirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login as auth_login ,logout
from django.contrib.auth import get_user_model
import datetime
from django.template import RequestContext, Template,Context
from time import ctime
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from common.log_api import *
from oms_api import *

def IsLogin(func):
    def isLogin(request,*args,**kwargs):
        if request.session.get('login_username'):
            return func(request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/login')
    return isLogin

def login(request):
    path = request.get_full_path()
    msg = request.GET.get('msg','')
    error = error = request.GET.get('error','')
    if request.method=='POST':
        data = request.POST
        username = data['Username']
        password = data['Password']
        if password == 'yuntai#123456':
            auth_user = authenticate(username=username,password=password)
            if auth_user is not None and auth_user.is_active:
                auth_login(request,auth_user)
                error = u"您的密码为初始密码，请修改密码后登录"
                return HttpResponseRedirect('/omsapp/change_pass/?error=%s' % error)
            else:
                error = u"用户名或密码错误"
        else:
            auth_user = authenticate(username=username,password=password)
            if auth_user is not None:
                if auth_user.is_active:
                    auth_login(request,auth_user)
                    response = HttpResponseRedirect('/zabbix/dashboard')
                    #response.set_cookie('username',username,3600)
                    #request.session['login_username'] = username
                    userlog_add(request.user,"用户：%s 登录成功" % request.user)
                    return response
                    #return render(request,"index.html",{})
                   # else:
                   #     request.session['login_username'] = 'admin'
                   #     error = u"用户名或密码错误"
                   #     return render(request,'login.html',{'error':error})
           
                else:
                    error = u"用户被锁定，请联系管理员"
            #return render(request,'login.html',{'error':error})
            else:
                #request.session['login_username'] = 'admin'
                error = u"用户名或密码错误"
            #return render(request,'login.html',{'error':error})
    return render(request,'login.html',{'error':error,'msg':msg})


@login_required
#@IsLogin
def oms(request):
    from django.template.loader import get_template
    username = request.user
    perms_list = request.user.get_all_permissions()
    logger.debug("%sperms_list" % perms_list)

    logger.debug("%s登录" % request.user)
    logger.debug("%s权限" % request.user.has_perms('auth.add_group'))
    return render(request,'index.html',{'username':username})
    #return HttpResponse(template.render(context))

@login_required
def oms_index3(request):

    logger.debug("%s登录" % request.user)
    return render(request,"index3.html",{})




def logout_view(request):
    logout(request)
    #try:
    #    del request.session['login_username']
    #except KeyError:
    #    pass
    return HttpResponseRedirect('/login')

