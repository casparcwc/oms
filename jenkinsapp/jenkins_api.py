#encoding:utf-8
'''
jenkins api
'''
import jenkins
import time
import sys
import os
import signal
import django
sys.path.append('../')
import chardet
from common.mysqlcon import jenkinsMysql
from redisapp.redis_api import RedisApi
from common.log_api import *
from django.db.models import Q,Count
from models import *

reload(sys)
sys.setdefaultencoding('utf-8')

class JenkinsApi(object):
    '''
    use jenkinsapi operate jenkins.
    '''

    def __init__(self):
        '''
        jenkins connection config
        '''
        self.__jenkins_server_url = 'http://127.0.0.1:8888'
        self.__user_id = 'chenwc30082'
        self.__password = 'e3acce2a1cd7da31c7bc73b73b242150'
        #self.job_name = job_name
        try: 
            self.jenkins_server = jenkins.Jenkins(self.__jenkins_server_url,username=self.__user_id,password=self.__password)
        except JenkinsException,e:
            raise e
        else:
            logger.info("self.jenkins_server connect success!")

    def get_version(self):
        '''
        get jenkins version
        '''
        return self.jenkins_server.version

    def jbuild(self,job_name,parameters):
        '''
        jenkins build job
        job_name: str
        parameters: dict
        '''
        try:
            self.this_build_number = self.jenkins_server.get_job_info(job_name,depth=0, fetch_all_builds=False)['nextBuildNumber']
            logger.debug(job_name+' build_number:'+str(self.this_build_number))
            self.jenkins_server.build_job(job_name,parameters)
            time.sleep(10)
        except Exception,e:
            logger.error(str(e))
            raise Exception(e)

    def get_console(self,servicename):
        '''
        get jenkins job  build console
        servicename: str, eg: yt-med-restapi
        '''

        #sql = "SELECT install_job_name from service_jobs_manager WHERE service_name like '%%s%' " % servicename
        #logger.debug('get_console sql :'+sql)
        #data = jenkinsMysql(sql)
        #install_job = '%s'%data[0]['install_job_name']
        data = ServiceJobsManager.objects.filter(Q(service_name__contains=servicename))
        install_job = data[0].install_job_name
        #install_job1 = ServiceJobsManager.objects.filter(service_name=servicename)
        #install_job = install_job1[0].install_job_name
        logger.debug("get_console install_job:%s"%install_job)
        #print type(install_job)
        install_build_number = self.jenkins_server.get_job_info(install_job)['lastBuild']['number']
        print install_build_number
        consoletxt = self.jenkins_server.get_build_console_output(install_job,install_build_number)
        #print type(consoletxt)
        #print consoletxt
        return consoletxt.decode('GB2312').encode('utf-8')

    def is_building(self,servicename,product):
        '''
        get service is_building status:
        return True or False 
        '''
        
        if 'install-deploy' in servicename:
            install_job = servicename
        else:
            #sql = "SELECT install_job_name from service_jobs_manager WHERE service_name like '%s' and product='%s'" % (servicename,product)
            #data = jenkinsMysql(sql)
            data = ServiceJobsManager.objects.filter(Q(service_name__contains=servicename))
            if not data:
                raise jenkins.JenkinsException('service name is not exists')
            else:
                install_job = data[0].install_job_name
                logger.info("install_job:%s"%install_job)
        try:
            time.sleep(5)
            install_build_number = self.jenkins_server.get_job_info(install_job)['lastBuild']['number']
            build_status = self.jenkins_server.get_build_info(install_job,install_build_number)['building']
            #print "build_status:%s"%build_status
            return build_status
        except Exception,error:
            logger.error(error)
            raise Exception(error)
    
    def base_is_building(self,basename):
        '''
        get base class is_building status:
        return True or False 
        '''
        #sql = "select install_job_name from svn_address_jobs_maps where nickname='%s'" % basename
        #data = jenkinsMysql(sql)
        #install_job = '%s'%data[0]['install_job_name']
        #print "install_job:%s"%install_job
        data = SvnAddressJobsMaps.objects.filter(Q(nickname__contains=basename))
        install_job = data[0].install_job_name
        try:
            install_build_number = self.jenkins_server.get_job_info(install_job)['lastBuild']['number']
            build_status = self.jenkins_server.get_build_info(install_job,install_build_number)['building']
            #print "build_status:%s"%build_status
            return build_status
        except Exception,error:
            logger.error(error)
            raise Exception(error)
        
    def build_status(self,servicename):
        '''
        get service building result:
        eg:return  successs or failed 
        '''
        #sql = "SELECT install_job_name from service_jobs_manager WHERE service_name='%s' " % servicename
        #print sql
        #data = jenkinsMysql(sql)
        #install_job = '%s'%data[0]['install_job_name']
        data = ServiceJobsManager.objects.filter(Q(service_name__contains=servicename))
        install_job = data[0].install_job_name
        try:
            install_build_number = self.jenkins_server.get_job_info(install_job)['lastBuild']['number']
            build_status = self.jenkins_server.get_build_info(install_job,install_build_number)['result']
            #print install_build_number
            #print "build_status:%s"%build_status
            return build_status
        except Exception,error:
            raise Exception(error)
            
    def get_num_now(self,job_name):
        install_build_number = self.jenkins_server.get_job_info(job_name)['lastBuild']['number']
        return install_build_number

    def deploy_status(self,job_name,install_build_number):
        '''
        get job build status 
        '''
        #time.sleep(10)
        #print self.this_build_number
        #install_build_number = self.jenkins_server.get_job_info(job_name)['lastBuild']['number']
        result = self.jenkins_server.get_build_info(job_name,install_build_number)['result']
        if result == None:
            return "Deploying"
        else:
            return result
    def create_servicejob(self,servicename,env='uat',servicetype='service'):
        '''
         create a new job with demo config.
        '''
        democonf = self.jenkins_server.get_job_config('uat-install-service-demo')
        jobconfig = democonf.replace('service-demo',servicename)
        if servicetype == 'war': 
            jobconfig = jobconfig.replace('target/*.zip','target/*.war')
        jobname = 'uat-install-'+servicename
        if self.jenkins_server.job_exists(jobname):
            raise jenkins.JenkinsException('jenkins job[%s] already exist'%jobname)
        try:
            self.jenkins_server.create_job(jobname,jobconfig)
        except jenkins.JenkinsException,e:
            raise jenkins.JenkinsException(e)
        else:
            logger.info("create servicejob %s success"%jobname)
            return jobname
    

def buildstatus_child(servicename,product):
    '''
    buildstatus child process 
    '''
    try:
        server = JenkinsApi()
        redis_server = RedisApi('dev',12)
    except Exception,e:
        #print e
        raise Exception(e)
    else:
        nu = 0
        logger.info("pip-all-install-deploy-in-Oms server.is_building :%s" % server.is_building('pip-all-install-deploy-in-Oms',product))
        oms_build_number = server.get_num_now('pip-all-install-deploy-in-Oms')
        while True:
            #time.sleep(1)
            if server.is_building('pip-all-install-deploy-in-Oms',product):
                if server.is_building(servicename,product) and nu < 99:
                    nu += 10
                    server_build_status = 'budling'
                    if server.is_building(servicename,product) and nu > 99:
                        nu = 99
                        server_build_status = 'budling'
                elif not server.is_building(servicename,product):
                    nu = 100
                    server_build_status = server.build_status(servicename) 
                deploy_status = server.deploy_status('pip-all-install-deploy-in-Oms',oms_build_number)
                status_dict = {'prognu':nu,'build_status':server_build_status,'deploy_status':deploy_status}
                redis_server.rcli.hset('Jenkins:BuildStatus',servicename,status_dict)
                logger.debug( "redis_server.rcli.hset Jenkins:BuildStatus %s %s"%(servicename,status_dict))
                logger.debug(redis_server.rcli.hgetall('Jenkins:BuildStatus'))
            else:
                nu = 100
                server_build_status = server.build_status(servicename)
                deploy_status = server.deploy_status('pip-all-install-deploy-in-Oms',oms_build_number)
                status_dict = {'prognu':nu,'build_status':server_build_status,'deploy_status':deploy_status}
                redis_server.rcli.hset('Jenkins:BuildStatus',servicename,status_dict)
                redis_server.rcli.expire('Jenkins:BuildStatus',1800)
                logger.debug( redis_server.rcli.hgetall('Jenkins:BuildStatus'))
                break
    print "i am child pid:%s,ppid:%s"%(os.getpid(),os.getppid()) 
    os._exit(0)
                 
def buildstatus_main(servicename):
    newpid = os.fork()
    if newpid == 0:
        buildstatus_child(servicename)


def select_nickname():
    #nickname_sql = 'select nickname from svn_address_jobs_maps where install_job_name is not null and svn_address is not null GROUP BY nickname'
    #data = jenkinsMysql(nickname_sql)
    #data = SvnAddressJobsMaps.objects.filter(Q(install_job_name__isnull=False),Q(svn_address__isnull=False)).values('nickname').annotate(count=Count('nickname'))
    data = SvnAddressJobsMaps.objects.filter(Q(install_job_name__isnull=False),Q(svn_address__isnull=False)).values('nickname').distinct()
    logger.debug(data.query)
    return data

def select_product():
    #product_sql = 'select product from svn_address_jobs_maps where svn_address is not null GROUP BY product'
    data = SvnAddressJobsMaps.objects.filter(Q(svn_address__isnull=False)).values('product').distinct()
    logger.debug(data.query)
    return data
    


if __name__ == "__main__":
    parame_dict={u'Enviroment':u'uat',u'TrunkOrBranch':u'T',u'Nickname':'',u'Projectname':u'upp-ms-notice',u'Product':u'openapi',u'Version':u'1.0.0'}
    server = JenkinsApi()
    #print parame_dict
    #print server.jbuild('pip-all-install-deploy-in-Oms',parame_dict)
    print server.get_console('ms-notice')
    #print server.deploy_status('pip-all-install-deploy-in-Oms')
    #print server.is_building('notice')
    #buildstatus_main('upp-ms-notice')
    
    #conff = server.create_servicejob('hs-med-testtest111111-web','web')
    #print conff
    print select_nickname()
