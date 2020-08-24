#encoding:utf-8
'''
zabbix data views
'''
import json
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from common.log_api import *
from zabbix import *
from models import *
from django.db.models import Q
from django.db.models import Count, Min, Max, Sum
import datetime
from time import ctime
from django.contrib.auth.decorators import login_required



@login_required
def omsTables(request):
    print 'starting','at',ctime()
    username = request.user
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        zabbix = Zabbix_Api()
    except Exception,e:
        print e
        error = e
        context = {'time':time,'error':error}
    else:
        cpudata = MyThread(zabbix.get_zabbixData,('CPU-IDLE%',),zabbix.get_zabbixData.__name__)
        memdata = MyThread(zabbix.get_zabbixData,('MEM-USED%',),zabbix.get_zabbixData.__name__)
        diskdata = MyThread(zabbix.get_zabbixData,('DISK-USED%',),zabbix.get_zabbixData.__name__)
        threads = [cpudata,memdata,diskdata]
        numthreads = range(len(threads))
        for i in numthreads:
            threads[i].start()
        for i in numthreads:
            threads[i].join()
        cpulist = cpudata.getResult()
        memlist = memdata.getResult()
        disklist = diskdata.getResult()
        #print cpulist,memlist,disklist
        for i in cpulist:
            i['cpu_value'] = i['value']
            for n in memlist:
                if i['hostid'] == n['hostid']:
                    i['mem_value'] = n['value']
            for m in disklist:
                if i['hostid'] == m['hostid']:
                    i['disk_value'] = m['value']
    
        #print cpulist
        #for i in datalist:
        #    for k,v in i.items():
        #        dic.setdefault(k,[]).append(v)
        #print dic
        context = {'cpulist':cpulist,'time':time}
    print 'ending','at',ctime()
    return render(request,"zabbix/tables_hosts.html",context)

#xiehe tables
@login_required
def omsTablesXh(request):
    username = request.user
    zabbix = Zabbix_Api_Xh()
    cpudata = MyThread(zabbix.get_xhzabbixData,('CPU-IDLE%',),zabbix.get_xhzabbixData.__name__)
    memdata = MyThread(zabbix.get_xhzabbixData,('MEM-USED%',),zabbix.get_xhzabbixData.__name__)
    diskdata = MyThread(zabbix.get_xhzabbixData,('DISK-USED%',),zabbix.get_xhzabbixData.__name__)
    threads = [cpudata,memdata,diskdata]
    numthreads = range(len(threads))
    for i in numthreads:
        threads[i].start()
    for i in numthreads:
        threads[i].join()
    cpulist = cpudata.getResult()
    memlist = memdata.getResult()
    disklist = diskdata.getResult()
    #print cpulist,memlist,disklist
    for i in cpulist:
        i['cpu_value'] = i['value']
        for n in memlist:
            if i['hostid'] == n['hostid']:
                i['mem_value'] = n['value']
        for m in disklist:
            if i['hostid'] == m['hostid']:
                i['disk_value'] = m['value']
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
    return render(request,"zabbix/tables_xh.html",{'username':username,'cpulist':cpulist,'time':time})



@login_required
def zabbixHosts(request):
    
    hosts_ip = ZInterface.objects.all().filter(main=1)
    host_info_list = []
    for hostobj in hosts_ip:
        hostdict = {}
        hostdict['hostname'] = hostobj.hostid.name
        hostdict['hostip'] = hostobj.ip
        host_info_list.append(hostdict)
    
    logger.debug('host_info_list：%s'%host_info_list)
    context = {'host_info_list':host_info_list}
    

    if request.GET.get('get_host_info',''):
        return host_info_list
    else:
        return render(request,"zabbix/hosts_info.html",context)


def zabbixTiggerApi(request):
    ztigger_dict={'disaster':0,'high':0,'average':0,'warring':0,'information':0,'notclassfield':0} 
    ######
    ztrigger_sql = '''SELECT DISTINCT host,ip.ip,hosts.name,t.description, 
                      f.triggerid,i.itemid,hosts.hostid,e.acknowledged, t.value,t.priority,FROM_UNIXTIME(t.lastchange) as lasttime 
                      FROM triggers t
                      INNER JOIN functions f ON ( f.triggerid = t.triggerid )
                      INNER JOIN items i ON ( i.itemid = f.itemid )
                      INNER JOIN hosts ON ( i.hostid = hosts.hostid )
                      INNER JOIN events e ON ( e.objectid = t.triggerid )
                      INNER JOIN interface ip ON ( ip.hostid = hosts.hostid )
                      WHERE (e.eventid DIV 100000000000000)
                      IN (0)
                      AND e.object=0
                      AND (t.value=1 OR (t.value =0 AND unix_timestamp(now()) - t.lastchange <60))
                      AND hosts.status =0
                      AND i.status =0
                      AND t.status =0
                      GROUP BY f.triggerid
                      ORDER BY t.lastchange DESC'''
    priority_sql = "select *,COUNT(1) as priority__count from (%s)a GROUP BY priority;"%ztrigger_sql

    ztrigger_data = ZTriggers.objects.raw(ztrigger_sql)
    #logger.debug("---ztrigger_data-raw--%s"%ztrigger_data) 

    priority_data = ZTriggers.objects.raw(priority_sql)
    for pd in priority_data:
        #logger.debug("---priority_data-pd--:%s"%pd)
        if pd.priority==5:
            ztigger_dict['disaster']+=pd.priority__count
        if pd.priority==4:
            ztigger_dict['high']+=pd.priority__count
        if pd.priority==3:
            ztigger_dict['average']+=pd.priority__count
        if pd.priority==2:
            ztigger_dict['warring']+=pd.priority__count
        if pd.priority==1:
            ztigger_dict['information']+=pd.priority__count
        if pd.priority==0:
            ztigger_dict['notclassfield']+=pd.priority__count
    #ztiggers = ZTriggers.objects.all().filter(state=0).values('priority').annotate(Count('priority')).order_by('-priority')
    #context = {"ztiggers":ztiggers}
    #logger.debug("zabbixTiggerApi data : %s"%ztiggers)
    #for i in ztigger:
    
    #####
    if request.method == "POST":
        logger.debug("--Method:POST--result:%s"%ztigger_dict)
        #return HttpResponse(json.dumps(ztigger_dict,sort_keys=True,indent=4,ensure_ascii=False))
        return JsonResponse(ztigger_dict,safe=False)
    elif request.method == "GET":
        logger.debug("--Method:GET-ztrigger_data-result : %s"%ztrigger_data)
        
        #获取zabbix采集数据的频率
        qps_sql = '''SELECT SUM(CAST(1.0/i.delay AS DECIMAL(20,10)))AS qps,i.itemid
                     FROM items i,hosts h
                     WHERE i.status=0
                     AND i.hostid=h.hostid
                     AND h.status=0
                     AND i.delay<>0
                     AND i.flags<>0x2'''
        qpsdata=ZItems.objects.raw(qps_sql)[0]
        
        #获取主机数量
        hosts_count_sql = '''SELECT hostid,count(1) as hosts_count from hosts WHERE status=0''' 
        hosts_count = ZHosts.objects.raw(hosts_count_sql)[0]
        logger.debug('hosts_count:%s'%hosts_count)        

        #获取redis连接数
        redis_clients_sql = '''SELECT itemid,value from history_uint WHERE itemid='25149' ORDER BY clock DESC limit 1'''
        redis_clients_con = ZHistoryUint.objects.raw(redis_clients_sql)[0]
        logger.debug('redis_clients_con:%s'%redis_clients_con.value)
        
        context = {"ztigger_dict":ztigger_dict,"ztrigger_data":ztrigger_data,'qpsdata':qpsdata,'hosts_count':hosts_count,'redis_clients':redis_clients_con}

        return render(request,"zabbix/zdashboard.html",context)
    else:
         return HttpResponse("请求错误")


def qpsGet(request):
    for i in qpsdata:
        print i
    return HttpResponse(json.dumps(qpsdata,sort_keys=True,indent=4,ensure_ascii=False))
def zabbixDashboard(request):
    
    ztiggers = ZTriggers.objects.all().filter(state=0).values('priority').annotate(Count('priority')).order_by('-priority')
    context = {"ztiggers":ztiggers}
    logger.debug("ztiggers data : %s"%ztiggers)
    return render(request,"zabbix/zdashboard.html",context)


