#encoding:utf-8

import json
from django.shortcuts import render
from common.log_api import *
from oms.oms_api import userlog_add,OmsError
from redis_api import *
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def redis_info(request):
    '''
    Get redis info.
    '''
    error = ''
    if request.method == 'POST':
        env = request.POST.get('redisenv','')
        db = request.POST.get('redisdb',0)
        try:
            Redis = RedisApi(env,db)
            redisinfo = Redis.info()
            logger.debug("redis env :%s connection success" % env)
            context = {'redisinfo':redisinfo}
        except Exception,e:
            error = e 
            context = {'error':error}
            logger.error("%s redis error: %s" % (env,error))
    else:
        try:
            Redis = RedisApi('uat',0)
            redisinfo = Redis.info()
            context = {'redisinfo':redisinfo}
        except Exception,e:
            error = e
            context = {'error':error}
            logger.error("%s redis error: %s" % ('uat',error))
        
    return render(request,'redis/redis.html',context)


@login_required
def redis_keys(request):
    '''
    Get redis keys and values.
    '''
    context = {}
    error = ''
    keys_values = []
    if request.method == 'POST':
        env = request.POST.get('redisenv','')
        key = request.POST.get('rediskey','')
        db = request.POST.get('redisdb','')
        try:
            Redis = RedisApi(env,db)
            keys = Redis.selectkey(key)
            logger.info("redis env :%s connection success" % env)
        except Exception,e:
            error = e
            logger.error("%s redis error: %s" % (env,error)) 
            
        #logger.debug("redis keys :%s " % keys)
        else:
            try:
                for k in keys:
                    dict_keys={}
                    value = Redis.getvalue(k)
                    type = Redis.gettype(k)
                    dict_keys['keyname']=k
                    dict_keys['value']=value
                    dict_keys['type']=type
                    keys_values.append(dict_keys)
                    #values.append(value)
                    #logger.debug("redis values :%s " % values)
                    #keys_values = dict(zip(keys,values))
                logger.info("get redis keys_values success and keys_values length:%s"%len(keys_values))
            except Exception,e:
                error = e
        context = {'key':key,'keys_values':keys_values,'error':error}
        #logger.debug("context:%s" % context)
    return render(request,'redis/redis_keys.html',context) 


