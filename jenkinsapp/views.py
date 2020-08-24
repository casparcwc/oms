# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import signal
import time
import json
import sys    
import MySQLdb
from django.shortcuts import render,redirect
#from django.shortcuts import render_to_response
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.urls import reverse
from common.log_api import *
from oms.oms_api import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from common.mysqlcon import *
from models import *
from jenkins_api import *
from redisapp.redis_api import RedisApi
from dwebsocket.decorators import accept_websocket, require_websocket
import time
reload(sys)
sys.setdefaultencoding('utf-8')


@login_required
def jdata(request):
    time = ''
    error = ''
    if request.method == "POST":
        time = request.POST['select_time']
        starttime = time.split(' - ')[0]
        endtime = time.split(' - ')[1]
        sql = "SELECT  belong_project as 'service_name',count(*) as 'deploy_count' from operation_log WHERE do_action='deploy' and op_environment='uat' and CREATE_TIME >= '%s' and CREATE_TIME <= '%s' GROUP BY belong_project;" % (starttime,endtime)
        sql1 = "SELECT  belong_project as 'service_name',count(*) as 'deploy_count' from operation_log WHERE do_action='deploy' and op_environment like '%%prd%%' and CREATE_TIME >= '%s' and CREATE_TIME <= '%s' GROUP BY belong_project;" % (starttime,endtime)
    else:
        sql = '''SELECT  belong_project as 'service_name',count(*) as 'deploy_count' from operation_log WHERE do_action='deploy' and op_environment='uat' and CREATE_TIME BETWEEN  DATE_ADD(now(), INTERVAL -1 DAY) and DATE_ADD(now(), INTERVAL 1 DAY) GROUP BY belong_project;'''
        sql1 = '''SELECT  belong_project as 'service_name',count(*) as 'deploy_count' from operation_log WHERE do_action='deploy' and op_environment like '%%prd%%' and CREATE_TIME BETWEEN  DATE_ADD(now(), INTERVAL -1 DAY) and DATE_ADD(now(), INTERVAL 1 DAY) GROUP BY belong_project;'''
    #logger.debug("[SQL]-%s" % sql1)
    try:
        data = jenkinsMysql(sql)
        data1 = jenkinsMysql(sql1)
    except Exception,error:
        logger.error("[Error]-%s" % error)
        context = {'error':error}
    else:
        datakeys = []
        datakeys1 = []
        datavalues = []
        datavalues1 = []
        for i in data:
            datakeys.append(i['service_name'].encode('utf-8'))
            datavalues.append(int(i['deploy_count']))
        for j in data1:
            datakeys1.append(j['service_name'].encode('utf-8'))
            datavalues1.append(int(j['deploy_count']))
        logger.debug("[jenkins data UAT]--datakeys:%s,datavalues:%s" % (datakeys,datavalues))
        logger.debug("[jenkins data PRD]--datakeys1:%s,datavalues1:%s" % (datakeys1,datavalues1))
                  

        context = {'error':error,'time':time,'datakeys':datakeys,'datavalues':datavalues,'datakeys1':datakeys1,'datavalues1':datavalues1,}
    return render(request,"jenkins/jenkinsdata.html",context)



def jinstall(request):
    error = '' 
    context = {}
    nicknamelist = select_nickname()
    productlist = select_product()
    if request.method == "POST":
        Environment = request.POST['Environment']
        TrunkorBronch = request.POST['TrunkOrBranch']
        Nickname = request.POST['Nickname']
        Version = request.POST['Version']
        Projectname = request.POST['Projectname']
        Product = request.POST['Product']
        Deployflag = request.POST.get('Deployflag','False')
                
        parame_dict = {'Enviroment':Environment,'TrunkOrBranch':TrunkorBronch,'Nickname':Nickname,
                       'Projectname':Projectname,'Product':Product,'Version':Version,
                       'Deployflag':Deployflag
                      }
        logger.debug("build parame_dict:%s"%parame_dict)
        servicelist = Projectname.split(',')
        logger.debug("servicelist:%s"%servicelist)
        build = ''
        deploy_status=''
        try:
            server = JenkinsApi()
            redis_server = RedisApi('dev',12)
            build = server.jbuild('pip-all-install-deploy-in-Oms',parame_dict)
            status_dict = {'prognu':0,'build_status':'building','deploy_status':'deploying'}
            for name in servicelist:
                redis_server.rcli.hset('Jenkins:BuildStatus',name,status_dict) 
                newpid = os.fork()
                if newpid == 0:
                    logger.debug("start buildstatus_child %s "%name)
                    buildstatus_child(name,Product)
            else:
                #if parame_dict['Deployflag']:
                    #deploy_status = server.deploy_status('pip-all-install-deploy-in-Oms')
                    #logger.debug('server.deploy_status:%s'%deploy_status)
            #logger.debug('-----build:%s' % build)
                
                #context = {'error':error,'msg':'start build %s'%servicelist}
                #context = {'servicelist':servicelist}
                return HttpResponseRedirect('/jenkins/jbuild_prog/')
        except Exception,e:
            error = "JenkinsApi Error："+str(e)
            logger.error(error)
            context = {'error':error,'msg':build}
        
        #return render(request,"jenkins/install_list.html",context) 
        #return HttpResponseRedirect(reverse('jbuild_prog', context))
    else:
        context = {'nicknamelist':nicknamelist,'productlist':productlist}
    return render(request,"jenkins/jenkinsinstall.html",context) 


@accept_websocket
def build_prog(request):
    '''
     websocket 进度条
    '''
    
    if not request.is_websocket():  # 判断是不是websocket连接
        try:  # 如果是普通的http方法
            uncontext = request.GET['context']
            u8context = uncontext.encode('utf-8')
            context = json.loads(u8context)
            logger.debug('not request.is_websocket:%si and type is:%s'%(context,type(context)))
            return render(request,'jenkins/install_list.html',context)
            #return HttpResponse(message)
        except:
            uncontext = request.GET['context']
            u8context = uncontext.encode('utf-8')
            logger.debug('u8context:%si and type :%s'%(u8context,type(u8context)))
            context = eval(u8context)
            logger.debug('not request.is_websocket:%si and type is:%s'%(context,type(context)))
            return render(request,'jenkins/install_list.html',context)
    else:
        server = JenkinsApi()
        logger.debug('request.websocket:%s'%request.websocket)
        nu = 0
        for service_names in request.websocket:
            service_name = service_names.split(',')
            logger.debug('request.websocket.servicename:%s and type is :%s'%(service_name,type(service_name)))
            for name in service_name:
                while True:
                    nu += 5
                    time.sleep(1)
                    logger.debug('request.websocket.servicename:%s and type is :%s'%(name,type(name)))
                    if server.is_building(name) and nu < 100:
                        logger.debug("nu:%s"%nu)
                        request.websocket.send(str(nu).encode('utf-8'))  # 发送消息到客户端 
                    if server.is_building(name) and nu >= 100:
                        request.websocket.send('99'.encode('utf-8'))
                        logger.debug("nu:%s"%nu)
                    if not server.is_building(name):
                        request.websocket.send('100'.encode('utf-8'))
                        logger.debug("server building done request.websocket.send:%s"% 100)
                        request.websocket.close()
                        break

@accept_websocket
def build_prog2(request):
    '''
     从redis中获取Jenkins:BuildStatus
    '''
    #if request.method == "GET":
    redis_server = RedisApi('dev',12)
    servicelist_redis = redis_server.rcli.hgetall('Jenkins:BuildStatus')
    servicestatus = {}
    for k, v in servicelist_redis.iteritems():
        value = eval(v)
        servicestatus[k] = value
    logger.debug("redis servicelist_redis :%s"%servicestatus)
    context = {'servicestatus':servicestatus,'servicelist':[]}
    return render(request,"jenkins/install_list.html",context)

def jconsole(request):
    context = {}
    if request.method == "GET":
        servicename = request.GET.get('servicename','')
        server =  JenkinsApi()
        console = server.get_console(servicename)
        context = {'console':console}
    return render(request,"jenkins/jenkinsconsole.html",context)
    

    


def createNewJob(request):
    error = ''
    msg = []
    waring = []
    context = {}
    if request.method == "POST": 
        servicename = request.POST['servicename']
        servicetype = request.POST['servicetype']
        trunk_or_branch = request.POST.get('TrunkOrBranch','')
        deploy_path = request.POST.get('deploy_path','')
        environment = request.POST.get('environment','')
        tomcat_path = request.POST.get('tomcat_path','')
        product = request.POST.get('product','')
        nickname = request.POST.get('nickname','')
        serverusername = request.POST.get('serverusername','hsyun')
        serverips = request.POST.get('serverip')
        base_install_job_name = request.POST.get('base_install_job_name','')
        log_level = request.POST.get('log_level','')  
        svn_address = request.POST.get('svn_address','')
        newjenkinsjobflag = request.POST.get('newjenkinsjobflag',False)
        adddatabaseflag = request.POST.get('adddatabaseflag',False) 
        if newjenkinsjobflag:
            try:
                server =  JenkinsApi()
                newjob = server.create_servicejob(servicename,servicetype)
                if newjob:
                    msg.append('create jenkinsjob %s success!'%servicename)
                    userlog_add(request.user,msg)
            except Exception,e:
                logger.error('Jenkins Error:[%s]'%e)
                return render(request,'jenkins/jenkinsnewjob.html',{'error':e,'msg':msg})
        if adddatabaseflag:
            newservicejob = 'uat-install-'+servicename
            SvnAddressJobsMaps_flag = nickname and svn_address
            ServiceJobsManager_flag = environment and product and nickname
            ServiceManager_flag = environment and serverips and product and serverusername 
            if SvnAddressJobsMaps_flag:# and not SvnAddressJobsMaps.objects.get(install_job_name='uat-install-'+servicename):
                try:
                    new_svnaddress=SvnAddressJobsMaps.objects.get_or_create(trunk_or_branch=trunk_or_branch,
                          product=product,nickname=nickname,svn_address=svn_address,install_job_name=base_install_job_name,
                          create_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                      )
                    if new_svnaddress:
                        msg.append('insert into SvnAddressJobsMaps success!')
                    else:
                        waring.append("new_svnaddress %s is already exists!"%nickname)
                        logger.warn("new_svnaddress %s is already exists!"%nickname)
                except Exception,e:
                    logger.error('Jenkins Database Error:[%s]'%e)
                    return render(request,'jenkins/jenkinsnewjob.html',{'error':e,'msg':msg})

            if ServiceJobsManager_flag:
                pkg_upload_path = '/package/med/cfg/'+nickname.lower()
                try:
                    new_servicejob = ServiceJobsManager.objects.get_or_create(env=environment,product=product,nickname=nickname,service_name=servicename,
                                     install_job_name=newservicejob,pkg_upload_path=pkg_upload_path,create_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                      )
                    if new_servicejob:
                        msg.append('insert into ServiceJobsManager success!')
                    else:
                        waring.append("new_servicejob %s is alreadly exists!"%servicename)
                        logger.warn("new_servicejob %s is alreadly exists"%servicename)
                except Exception,e:
                    logger.error('Jenkins Database Error:[%s]'%e)
                    return render(request,'jenkins/jenkinsnewjob.html',{'error':e,'msg':msg})

            if ServiceManager_flag:
                pkg_path = '/home/%s/package/%s'%(serverusername,servicetype)
                backup_path = '/home/%s/package/temp'%serverusername
                if not tomcat_path and servicetype=='war':
                    tomcat_path = '/data/ftp/tomcat-'+servicename
                if not deploy_path:
                    deploy_path = '/home/'+serverusername
                serverip_list = serverips.split(',')

                for serverip in serverip_list:
                    logger.debug('serverip:%s'%serverip)
                    try:
                        new_servicemanag = ServiceManager.objects.get_or_create(env=environment,ip=serverip,service_name=servicename,
                                  is_active='Y',product=product,name_type=servicetype,busi_type=product,load_flag=0,pkg_path=pkg_path,
                                  backup_path=backup_path,tomcat_path=tomcat_path,service_deploy_path=deploy_path,log_level=log_level,
                                  create_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                 )
                        if new_servicemanag:
                            msg.append('%s:%s:%s insert into ServiceManager success!'%(environment,serverip,servicename))
                        else:
                            waring.append("new_servicemanager %s:%s:%s:%s is already exists!"%(environment,serverip,servicename,product))
                            logger.warn(u"new_servicemanager %s:%s:%s:%s is already exists"%(environment,serverip,servicename,product)) 
                    except Exception,e:
                        error = e
                        logger.error('Jenkins Database Error:[%s]'%e)
            if not SvnAddressJobsMaps_flag and not ServiceJobsManager_flag and not ServiceManager_flag:
                error = u'写入数据库失败，请完整填写正确的信息'
                logger.error("写入数据库失败，请完整填写正确的信息")
            #userlog_add(request.user,msg)
             
        if not adddatabaseflag and not newjenkinsjobflag:
            error = '请选择：Create New Jenkins Job OR Add To Database'

        logger.info(msg)
         
    context = {'error':error,'waring':waring,'msg':msg}
    return render(request,"jenkins/jenkinsnewjob.html",context)


def get_ip_info(request):
    if request.method == 'POST':
        ip = request.POST.get('ip','')
        logger.debug("get_ip_info--%s"%ip)
        ipinfo={}
        service_name=[]
        if ip:
            try:
                ipinfo_obj = ServiceManager.objects.filter(ip=ip,is_active='Y')
            except Exception,e:
                logger.error('get_ip_info error:%s'%e)
            else:
                if ipinfo_obj:
                    for i in ipinfo_obj:
                        service_name.append(i.service_name)
                    ipinfo[i.ip]=service_name
                    return HttpResponse(json.dumps(ipinfo,sort_keys=True,indent=4,ensure_ascii=False))
                else:
                    return HttpResponse('null')
        else:
            return HttpResponse('null，请检查入参')
    else:
        return HttpResponse('error')
    
@login_required
def charJs(request):
    #return render(request,"chartjs.html",{'username':username})
    return render(request,"tables.html",{'username':username})



