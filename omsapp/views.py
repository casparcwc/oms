#-*- coding: utf-8 -*-
from django.shortcuts import render,redirect
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login as auth_login ,logout
from django.contrib.auth import get_user_model
from models import *
import time,datetime
from django.template import RequestContext, Template,Context
from time import ctime
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from common.log_api import *
from oms.oms_api import *


def change_pass(request):
    error = request.GET.get('error','')
    huser = request.GET.get('huser','')
    ntime = request.GET.get('ntime','')
    hash_encode = request.GET.get('hash_encode','')
    msg = ''
    logger.debug("change_pass request.user is_anonymous:%s"%request.user.is_anonymous)
    if request.user.is_anonymous:
        if hash_encode == md5_crypt(huser+ntime):
            if time.time() - float(ntime) > 600:
               return HttpResponse('链接超过10分钟，已失效！')
            
        else:
            return HttpResponse('<p style="color:red">拒绝访问！HASH 校验失败！</p>')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        real_name = request.POST['real_name']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        if password != password_confirm:
            error = '两次密码不匹配'
            logger.debug("修改密码：输入两次密码不匹配")
        else:
            try:
                userobj = omsUser.objects.get(username=username,email=email,real_name=real_name)
            except Exception:
                error = '用户信息校验失败'
                pass
            else:
                userobj.set_password(password)
                userobj.save()
                msg = '密码修改成功,请重新登录'
                userlog_add(request.user,'用户：%s 密码修改成功' % username)
                logger.debug('用户：%s 密码修改成功' % username)
                return HttpResponseRedirect('/login/?msg=%s' % msg)
    return render(request,'user/restpass.html',{'error':error,'msg':msg})
            
def forget_pass(request):
    error = ''
    msg =''
    hash_encode=''
    if request.method == 'POST':
        username = request.POST['Username']
        real_name = request.POST['Real_name']
        email = request.POST['Email']
        try:
            userobj = omsUser.objects.get(username=username,real_name=real_name,email=email)
        except Exception:
            error = '忘记密码，信息校验失败'
            pass
        else:
            auth_user = authenticate(username=username,password=userobj.password)
            ntime = str(time.time())
            huser = md5_crypt(username)
            hash_encode = md5_crypt(huser+ntime)
            mail_msg = u"""
               您好：%s
               密码修改地址：%s/omsapp/change_pass/?huser=%s&ntime=%s&hash_encode=%s
               提示：链接将于10分钟后失效,请尽快修改密码。 
               """% (real_name,SERVER_URL,huser,ntime,hash_encode) 
            send_mail('OMS用户密码修改',mail_msg,EMAIL_HOST_USER,[email],fail_silently=False)
            logger.debug("OMS用户[%s]密码修改邮件[%s]已发送"%(username,email))
            msg="邮件已发送，请查看邮件修改密码"
            return HttpResponse('%s' % msg)
    return render(request,'user/forget_pass.html',{'error':error,'msg':msg}) 

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import View
class GroupUser(PermissionRequiredMixin,View):
    '''
    Group Class Views
    '''
    # Or multiple of permissions:
    template_name = 'user/add_group.html'
    permission_required = ('auth.add_group')
    context_object_name = 'group_list'
    #@permission_required('auth.add_group',raise_exception = True )
    def get(self,request):
        #group_list = Group.objects.filter().order_by('name')
        group_list = Group.objects.all()
        perm_list = Permission.objects.all()
        #logger.debug('Get Group_list[%s] perm_list[%s] success!' % (group_list,perm_list))
        context = {'group_list':group_list,'perm_list':perm_list}
        return render(request,self.template_name,context)
    
    #@permission_required('oms.add_group',raise_exception=True)
    def post(self,request):
        error = '' 
        if request.method=='POST' and request.POST.has_key('addgroup'):
            groupname = request.POST['groupname']
            permid_list = request.POST.getlist('permid[]')
            new_group, created = Group.objects.get_or_create(name=groupname)
            ## create a permission
            for permid in permid_list:
                try:
                    new_group.permissions.add(int(permid))
                except Exception,e:
                    try:
                        new_group.delete()
                    except Exception:
                        pass
                    error = u"%s" % e
                    logger.error("添加用户组权限失败:%s" % error)
                    return HttpResponse('添加失败:[%s]' % error)
            logger.debug("Post add_group success and permissionid is:%s groupname is:%s" % (permid_list,groupname)) 
            userlog_add(request.user,"addgroup [%s] and permissionid is:%s,success" % (groupname,permid_list))
            return HttpResponse('success')
            #return HttpResponseRedirect('/omsapp/add_group')
            #context = {'group_list':self.group_list,'perm_list':self.perm_list,'error':error}
            #return render(request,self.template_name,context)

        #delete group
        if request.method=='POST' and request.POST.has_key('delgroup'):
            groupname = request.POST['groupname']
            group = Group.objects.get(name=groupname)
            group.delete()
            logger.debug("Delete group:%s success!" % groupname) 
            userlog_add(request.user,"Delete group:%s success!" % groupname)
            return HttpResponseRedirect('/omsapp/add_group')


@login_required
@permission_required('omsapp.add_omsuser',raise_exception = True )
def user_list(request):
    username = request.user
    user_list = omsUser.objects.all()
    error = request.GET.get('error','')
    msg = request.GET.get('msg','')
    return render(request,"user/user_list.html",{'username':username,'user_list':user_list,'error':error,'msg':msg})

@login_required
@permission_required('omsapp.add_omsuser',raise_exception = True )
def user_add(request):
    username = request.user
    path = request.get_full_path()
    error = ''
    msg = ''
    group_list = Group.objects.all()
    if request.method == 'POST':
        username = request.POST['username']
        real_name = request.POST['real_name']
        email = request.POST['email']
        phone_num = request.POST['phone_num']
        password = request.POST['password']
        groupnames = request.POST.getlist('groupname', [])
        is_active = request.POST.get('is_active',0)
        sendemail = request.POST.get('sendemail','')
        try:
            username_check_is_exist = omsUser.objects.filter(username=username)
            real_name_check_is_exist = omsUser.objects.filter(real_name=real_name)
            if username_check_is_exist:
                error = u'用户: %s 已存在' % username
                raise OmsError
            if real_name_check_is_exist:
                error = u'姓名: %s 已创建用户' % real_name
                raise OmsError
            for group_name in groupnames:
                group_name_check_is_exist = Group.objects.get(name=group_name)
                if not group_name_check_is_exist:
                    error = u'用户组:%s 不存在' % group_name
                    raise OmsError
        except OmsError:
            pass
        else:
            try:
                #create user
                new_user = omsUser.objects.create_user(username=username,real_name=real_name,email=email,phone_num=phone_num,password=password)
                logger.debug('create new_user:%s' % new_user)
                #add user to group
                if groupnames:
                    for groupname in groupnames:
                        new_user.groups.add(Group.objects.get(name=groupname).id)
                        logger.debug('Add new_user:%s to group:%s' % (new_user,groupname))
                        userlog_add(request.user,'Add new_user:%s to group:%s,success' % (new_user,groupname))
            except Exception,e:
                error = u'创建用户失败，Error:%s' % e
                logger.error("创建用户失败，Error：%s " % e)
                try:
                    new_user.delete()
                except Exception,e:
                    logger.error("Error:%s " % e)
                    pass
            else:
                logger.info("Add user:%s success!" % username)
                if new_user and sendemail:
                    mail_msg = u"""
                    您好：
                      您的用户名：%s
                      默认密码：%s
                      登录地址：%s/login/
                      请及时登录修改默认密码，如有问题请联系运维人员处理！
                    """ %(username,password,SERVER_URL)
                    try:
                        send_mail('您的OMS用户已创建',mail_msg,EMAIL_HOST_USER,[email],fail_silently=False)
                        msg = '用户创建成功,邮件已发送'
                        logger.debug("邮件发送成功:%s"%mail_msg)
                    except Exception,e:
                        error = u"用户创建成功,但是邮件发送失败,请确认邮箱地址是否正确！Error:%s" % e
                        logger.info("邮件已发送失败：[%s]" % e)
                elif new_user:
                    msg = '用户创建成功'
                return HttpResponseRedirect('/omsapp/user_list/?error=%s&msg=%s' % (error,msg))
    return render(request,"user/user_add.html",{'username':username,'error':error,'msg':msg,'group_list':group_list})

@login_required
def user_edit(request):
    error = ''
    if request.method == 'GET':
        username = request.GET.get('username', '')
        if not username:
            error = "请选择编辑用户"
        group_list = Group.objects.all()
        try:
            userobj = omsUser.objects.get(username=username)
        except Exception,e:
            error = '用户%s不存在:%s'%(username,e)
            context = {'error':error}
        else:
            real_name = userobj.real_name
            email = userobj.email
            phone_num = userobj.phone_num
            context = {'username':username,'real_name':real_name,'email':email,'phone_num':phone_num,'group_list':group_list,'error':error}
    if request.method == 'POST':
        username = request.POST['username']
        real_name = request.POST['real_name']
        email = request.POST['email']
        phone_num = request.POST['phone_num']
        groupnames = request.POST.getlist('groupname', [])
        is_active = request.POST.get('is_active',0)
        sendemail = request.POST.get('sendemail','')
        user_get = omsUser.objects.get(username=username)
        if user_get:
            user_get.real_name = real_name
            user_get.email = email
            user_get.phone_num = phone_num
            user_get.is_active = is_active
            user_get.save()
            #add user to group
            if groupnames:
                user_get.groups.clear() #clear old group
                for groupname in groupnames:
                    user_get.groups.add(Group.objects.get(name=groupname).id) #add new group
            logger.debug('---Edit %s success and group is:%s' % (username,','.join(groupnames)))
            userlog_add(request.user,'Edit %s information success and group is:%s' % (username,groupnames))
        return HttpResponseRedirect('/omsapp/user_list/')
    return render(request,"user/user_edit.html",context)

        

@login_required
def user_del(request,user=''):
    username = request.user
    msg = ''
    error = ''
    logger.debug("user:%s" % user)
    if request.method == "GET":
        user_ids = request.GET.get('user', '')
        user_id_list = user_ids.split(',')
        logger.debug("user_id_list:%s" % user_id_list)
    elif request.method == "POST":
        user_ids = request.POST.get('user', '')
        user_id_list = user_ids.split(',')
        logger.debug("user_id_list:%s" % user_id_list)
    for user_name in user_id_list:
        user = omsUser.objects.get(username=user_name)
        if user and user.username != 'admin':
            try:
                user.delete()
                logger.debug(u"成功删除用户 %s " % user.username)
                userlog_add(request.user,u"成功删除用户：%s " % user.username)
            except Exception,e:
                error = u"删除用户[%s]失败：%s" % ()
                raise OmsError
            else:
                msg = u"""
                用户:%s删除成功
                """ % user_id_list
    return HttpResponseRedirect('/omsapp/user_list?error=%s&msg=%s' % (error,msg))




def logout_view(request):
    logout(request)
    #try:
    #    del request.session['login_username']
    #except KeyError:
    #    pass
    return HttpResponseRedirect('/login')
