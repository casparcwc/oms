#! /usr/bin/python
#-*- coding:utf-8 -*-
'''
Created on 2016-9-9
@author: cc
 '''

import sys
import json
import urllib2
from urllib2 import URLError
import time
import threading
from time import ctime
from datetime import datetime
sys.path.append('../')

from common.log_api import *



class MyThread(threading.Thread):
    def __init__(self,func,args,name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
    def run(self):
        #print 'starting',self.name,'at',ctime()
        self.res = apply(self.func,self.args)
        #print 'ending',self.name,'at',ctime()
    def getResult(self):
        return self.res


def performance(f):
    def fn(*args, **kw):
        t_start = time.time()
        r = f(*args, **kw)
        t_end = time.time()
        print 'call %s() in %fs' % (f.__name__, (t_end - t_start)) 
        return r
    return fn 

class Zabbix_Api(object):
    def __init__(self):
        url = 'http://127.0.0.1/zabbix/api_jsonrpc.php'
        header = {"Content-Type":"application/json"}
        self.url = url
        self.header = header
        self.__auth = self.get_auth()
        self.hostid = self.get_host()

    def get_data(self,data):
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request,timeout=60)
            time.sleep(1)
        except URLError,e:
            if hasattr(e, 'reason'):
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'Error code: ', e.code
            raise Exception(e)
        else:
            response = json.loads(result.read())
            result.close()
            return response

    def get_auth(self):
        data = json.dumps({
               "jsonrpc": "2.0",
               "method": "user.login",
               "params": {
                   #"user": "Admin",
                   #"password": "chenweichao",
                   "user": "chenweichao",
                   "password": "hsyt30082chen",
                   "auth": "null"
               },
               "id": 0
            })
             # create request object
        response = self.get_data(data)
        if response.has_key('error'):
            error = response['error']
            logger.debug("Zabbix_Api get_auth error:%s"%error)
            raise Exception(error)
        else:
            return response['result']
 

        
    def get_host(self):
        data = json.dumps({
                "jsonrpc": "2.0",
                "method": "host.get",
                "params":{
                          "output": "extend",
                          #["hostid","name"],
                          "filter": ""
                          },
                "auth": self.__auth,
                "id": 1
                })
        response = self.get_data(data)
        hostlist = []
        for host in response['result']:
            hostlist.append(host)
        return hostlist
   
   #@performance
    def get_item(self,itename):
        data = json.dumps({
                "jsonrpc": "2.0",
                "method": "item.get",
                "params":{
                          "output": ["hostid","itemid",],
                          "filter": "",
                          #"hostids":hostid,
                          "monitored": "true",
                          "search": {
                                      "name": itename
                                    },
                          "sortfield": "name"
                          },

                "auth": self.__auth,
                "id": 1
                })
        response = self.get_data(data)
        item_id = []
        item_name = []
        item_dic = {}
        #print response
        #for itemName in itemlist:
        #    for item in response['result']:
        #        if item['name'] == itemName:
        #            item_id.append(item['itemid'])
        #            item_name.append(item['name'])
                    #item_dic[item['name']] = item['itemid']
        #    item['hostid']=hostid
        #    item_id.append(item)
        if response['result']:
            for item in response['result']:
            #item_id.append(item)
            #item_name.append(item['name'])
            #if item:
                item_id.append(item)
        else:                
            item_dic['hostid'] = hostid
            item_dic['itemid'] = ''
            item_id.append(item_dic)
        return item_id

        #print item['itemid'],item['name']
        #return item_dic
        #return item
   # @performance
    def get_history(self,itemid):
        result = []
        valuelist = []
        #for itemId in itemid:
            #for dataType in [0,1,3]:
        data = json.dumps({
                "jsonrpc": "2.0",
                "method": "history.get",
                "params": {
                    "output": "extend",
                    "history": [0,1,2,3],
                    #"hostids": hostid,
                    "itemids": itemid,
                    "sortfield": "clock",
                    "sortorder": "DESC",
                    #"search": {
                    #            "itemid": itemidlist,
                    #           },
                    "limit": 1
                },
                "auth": self.__auth,
                "id": 1
              })
        response = self.get_data(data)
        for value in response['result']:

            return value
            #valuelist.append(value)
        #return valuelist
        #print response['value']
        #result.append(response['value'])
        #print valuelist
        #for history in valuelist:
        #    return history
        #print response
        #return valuelist

   # @performance 
    def get_cpudata2(self):
        itename = "CPU-IDLE"
        itemid = []
        host_item = []
        cpudata = []
        for h in self.hostid:
            itemid = self.get_item(h['hostid'],itename)
            item_dct = {}
            if itemid:
                #print h,itemid
                item_dict = dict(h,**itemid)
                host_item.append(item_dict)
        for id in host_item:
            data = self.get_history(id['hostid'],id['itemid'])
            if data:
                cpudict = dict(id,**data)
                cpudata.append(cpudict)
        #print id,data
        return cpudata

    def get_cpudata(self):
        item = self.get_item('CPU-IDLE')
        host_item_list = []
        host_item_dict = {}
        cpudata = []
        for itid in item:
            for host in self.hostid:
                if itid['hostid'] == host['hostid']:
                    host_item_dict = dict(itid,**host)
                    host_item_list.append(host_item_dict)
        for id in host_item_list:
            #print id['itemid']
            data = self.get_history(id['itemid'])
            if data:
                cpudict = dict(id,**data)
                cpudata.append(cpudict)
        return cpudata
    
   
    
    def get_zabbixData(self,itemname):
        t_start = datetime.now()
        item = self.get_item(itemname)
        host_item_list = []
        host_item_dict = {}
        data = []
        datalist = []
        threads = []
       # def aa(itid):
       #     for host in self.hostid:
       #         if itid['hostid'] == host['hostid']:
       #             host_item_dict = dict(itid,**host)
       #             host_item_list.append(host_item_dict)


       #     return host_item_list
       # host_item_list=[aa(itid) for itid in item]
        for itid in item:
            for host in self.hostid:
                if itid['hostid'] == host['hostid']:
                    host_item_dict = dict(itid,**host)
                    host_item_list.append(host_item_dict)
        for id in host_item_list:
            #print id['itemid']
            the = MyThread(self.get_history,(id['itemid'],),self.get_history.__name__)
            threads.append(the)
        numthreads = range(len(threads))
        logger.debug('get %s data threads number is:%d' % (itemname,len(threads))) 
        for i in numthreads:
            threads[i].start()
        for i in numthreads:
            threads[i].join()
            if threads[i].getResult():
                data.append(threads[i].getResult())
        for id in host_item_list:
            for d in data:
                if id['itemid'] == d['itemid']:
            #getdata = self.get_history(id['itemid'])
            #if getdata:
                    datadict = dict(id,**d)
                    datalist.append(datadict)
        t_end = datetime.now()
        logger.debug('get %s data success! use time:%ss' % (itemname,(t_end-t_start).total_seconds()))
        return  datalist

#zabbix xiehe api
class Zabbix_Api_Xh(object):
    def __init__(self):
        #url = 'http://www.ezoperation.com/zabbix/api_jsonrpc.php'
        url = 'http://123.56.10.138/zabbix/api_jsonrpc.php'
        header = {"Content-Type":"application/json"}
        self.url = url
        self.header = header
        self.__auth = self.get_auth()
        self.hostid = self.get_host()

    def get_data(self,data):
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError,e:
            if hasattr(e, 'reason'):
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'Error code: ', e.code
            raise Exception(e)
        else:
            response = json.loads(result.read())
            result.close()
            return response

    def get_auth(self):
        data = json.dumps({
               "jsonrpc": "2.0",
               "method": "user.login",
               "params": {
                   "user": "Admin",
                   "password": "T44E_0lA",
                   "auth": "null"
               },
               "id": 0
            })
             # create request object
        response = self.get_data(data)
        if response.has_key('error'):
            error = response['error']
            logger.debug("Zabbix_Api get_auth error:%s"%error)
            raise Exception(error)
        else:
            return response['result']

        
    def get_host(self):
        data = json.dumps({
                "jsonrpc": "2.0",
                "method": "host.get",
                "params":{
                          "output": "extend",
                          #["hostid","name"],
                          "filter": ""
                          },
                "auth": self.__auth,
                "id": 1
                })
        response = self.get_data(data)
        hostlist = []
        for host in response['result']:
            hostlist.append(host)
        return hostlist
   
   #@performance
    def get_item(self,itename):
        data = json.dumps({
                "jsonrpc": "2.0",
                "method": "item.get",
                "params":{
                          "output": ["hostid","itemid",],
                          "filter": "",
                          #"hostids":hostid,
                          "monitored": "true",
                          "search": {
                                      "name": itename
                                    },
                          "sortfield": "name"
                          },

                "auth": self.__auth,
                "id": 1
                })
        response = self.get_data(data)
        item_id = []
        item_name = []
        item_dic = {}
        if response['result']:
            for item in response['result']:
                item_id.append(item)
        else:                
            item_dic['hostid'] = hostid
            item_dic['itemid'] = ''
            item_id.append(item_dic)
        return item_id

   # @performance
    def get_history(self,itemid):
        result = []
        valuelist = []
        data = json.dumps({
                "jsonrpc": "2.0",
                "method": "history.get",
                "params": {
                    "output": "extend",
                    "history": [0,1,2,3],
                    #"hostids": hostid,
                    "itemids": itemid,
                    "sortfield": "clock",
                    "sortorder": "DESC",
                    #"search": {
                    #            "itemid": itemidlist,
                    #           },
                    "limit": 1
                },
                "auth": self.__auth,
                "id": 1
              })
        response = self.get_data(data)
        for value in response['result']:
            return value

   # @performance 
    def get_cpudata2(self):
        itename = "CPU-IDLE"
        itemid = []
        host_item = []
        cpudata = []
        for h in self.hostid:
            itemid = self.get_item(h['hostid'],itename)
            item_dct = {}
            if itemid:
                #print h,itemid
                item_dict = dict(h,**itemid)
                host_item.append(item_dict)
        for id in host_item:
            data = self.get_history(id['hostid'],id['itemid'])
            if data:
                cpudict = dict(id,**data)
                cpudata.append(cpudict)
        #print id,data
        return cpudata

    def get_cpudata(self):
        item = self.get_item('CPU-IDLE')
        host_item_list = []
        host_item_dict = {}
        cpudata = []
        for itid in item:
            for host in self.hostid:
                if itid['hostid'] == host['hostid']:
                    host_item_dict = dict(itid,**host)
                    host_item_list.append(host_item_dict)
        for id in host_item_list:
            #print id['itemid']
            data = self.get_history(id['itemid'])
            if data:
                cpudict = dict(id,**data)
                cpudata.append(cpudict)
        return cpudata
    
   
    
    def get_xhzabbixData(self,itemname):
        t_start = datetime.now()
        item = self.get_item(itemname)
        host_item_list = []
        host_item_dict = {}
        data = []
        datalist = []
        threads = []
        for itid in item:
            for host in self.hostid:
                if itid['hostid'] == host['hostid']:
                    host_item_dict = dict(itid,**host)
                    host_item_list.append(host_item_dict)
        for id in host_item_list:
            #print id['itemid']
            the = MyThread(self.get_history,(id['itemid'],),self.get_history.__name__)
            threads.append(the)
        numthreads = range(len(threads))
        logger.debug('get %s data threads number is:%d' % (itemname,len(threads)))
        for i in numthreads:
            threads[i].start()
        for i in numthreads:
            threads[i].join()
            if threads[i].getResult():
                data.append(threads[i].getResult())
        for id in host_item_list:
            for d in data:
                if id['itemid'] == d['itemid']:

            #getdata = self.get_history(id['itemid'])
            #if getdata:
                    datadict = dict(id,**d)
                    datalist.append(datadict)
        t_end = datetime.now()
        logger.debug('get %s data success! use time:%ss' % (itemname,(t_end-t_start).total_seconds()))
        return  datalist



@performance
def getItem():
    threads = []
    zabbix = Zabbix_Api()
    itemlist =[]
    #cpudata = MyThread(zabbix.get_zabbixData,('CPU-IDLE',),zabbix.get_zabbixData.__name__)
    #memdata = MyThread(zabbix.get_zabbixData,('MEM-USED',),zabbix.get_zabbixData.__name__)
    #diskdata = MyThread(zabbix.get_zabbixData,('DISK-USED',),zabbix.get_zabbixData.__name__)
    #threads = [cpudata,memdata,diskdata]

    for i in zabbix.hostid:
        the = MyThread(zabbix.get_item,('CPU-IDLE',i['hostid'],),zabbix.get_item.__name__)
        threads.append(the)
        
    numthreads = range(len(threads))
    

    for i in numthreads:
        threads[i].start()
    for i in numthreads:
        threads[i].join()
        itemlist += threads[i].getResult()
    
    #print itemlist
    host_item_list = []
    host_item_dict = {}
    for host in zabbix.hostid:
        for itid in itemlist:
            if itid['hostid'] == host['hostid']:
                host_item_dict = dict(itid,**host)
                host_item_list.append(host_item_dict)
    return host_item_list
def getHistory():
    zabbix = Zabbix_Api()
    data = []
    datalist = []
    threads = []
    host_item_list = getItem()
    for id in host_item_list:
        #print id['itemid']
        the = MyThread(zabbix.get_history,(id['itemid'],),zabbix.get_history.__name__)
        threads.append(the)
    numthreads = range(len(threads))

    for i in numthreads:
        threads[i].start()
    for i in numthreads:
        threads[i].join()
        if threads[i].getResult():
            data.append(threads[i].getResult())
    for id in host_item_list:
        for d in data:
            if id['itemid'] == d['itemid']:

        #getdata = self.get_history(id['itemid'])
        #if getdata:
                datadict = dict(id,**d)
                datalist.append(datadict)
    return  datalist
 
    

if __name__ == '__main__':
    #print getItem()
    #print getHistory()
    zabbix = Zabbix_Api()
    #cpudata = zabbix.get_zabbixData('CPU-IDLE')
    #print cpudata
    #print memdata
  #  #main()
    item = zabbix.get_item('DISK-USED%')
    #history = zabbix.get_history(25472)
    #history2 = zabbix.get_history(25474)
    #history3 = zabbix.get_history(25470)
    #print zabbix.hostid
    diskdata = zabbix.get_zabbixData('DISK-USED')
    #cpudata = zabbix.get_zabbixData('CPU-IDLE')
    print item
    #print history,history2,history3
