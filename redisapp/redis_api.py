#econding:utf-8
'''
 redis api
'''
import sys
import redis
import json

class RedisApi(object):
    '''
    Redis connection class
    '''

    def __init__(self,env,db,port=6379):
        self.port = port
        self.db=db
        
        if env == "dev":
            self.host = "127.0.0.1"
            self.password = "redis"
        if env == "uat":
            self.host = "10.10.10.10"
            self.password = "eeee@redis"
        if env == "prd":
            self.host = ""
            self.password = ""

    #def conn(self):
        try:
            self.rcli = redis.StrictRedis(self.host,self.port,self.db,self.password,socket_timeout = 1)
        except Exception,e:
            logger.debug("redis connection error: %s" % e)
            raise e
        #    pass
    def info(self):
        '''
        return redis info
        '''
        return self.rcli.info()

    def selectkey(self,key):
        '''
        Fuzzy matching redis keys.
        return keys list.
        '''
        keys = []
        scan_it = self.rcli.scan_iter(match='%s*'%key,count=1000)
        try:
            while True:
                sel_key = scan_it.next()
                keys.append(sel_key)
        except StopIteration:
            pass
        except Exception,e:
            raise e
        return keys

    def gettype(self,key):
        '''
         get redis keys type
         return type
        '''
        try:
            type = self.rcli.type(key)
            return type
        except Exception,e:
            print e
            raise exception(e)
         
    def getvalue(self,key):
        '''
        Get values with redis key.
        return values
        '''
        try:
            type = self.rcli.type(key)
        except Exception,e:
            print e 
        else:
        #pipe = self.rcli.pipeline()
            if type == 'hash':
                #print type
                values = self.rcli.hgetall(key)
            elif type == 'list':
                #print type
                values = self.rcli.lrange(key,0,-1)
            elif type == 'set':
                #print type
                values = self.rcli.smembers(key)
            elif type == 'string':
                #print type
                values = self.rcli.get(key)
            else:
                #print type
                error = 'key type:%s is not support!' % type
                print error
                raise Exception(error)
            #result = pipe.execute()
            return values
    def delete_key(self,key):
    	'''
	 delete key
        '''		 
        scan_it = self.rcli.scan_iter(match=key, count=1000)
        while True:
            try:
                nextKey = scan_it.next()
                self.rcli.delete(nextKey)
            except StopIteration, e:
                break

if __name__ == "__main__":
    #env = sys.argv[1]
    #db = sys.argv[2]
    Redis_server = RedisApi('dev',12)
    print Redis_server.host
    #redis_cn = Redis.conn()
    #print Redis.info()
    #print type(redis_info)
    keys = Redis_server.selectkey('test')
    print keys
    for k in keys:
        Redis_server.delete_key(k)
        print "delete key:%s success"%k
    #print "connected_clients: %s" % redis_info['connected_clients']
    Redis_server.rcli.hset('install-name','upp-ms-ups',{'prognu':123,'status':'success'})
    values=Redis_server.hget("install-name","upp-ms-ups")
    #print redis_cn.hkeys("install-name")
    #print type(values)
    #value_dic=eval(values)
    #print value_dic['prognu']
    print values
    
