#ecoding:utf-8
'''
数据库操作
'''

import MySQLdb
import sys
import os


reload(sys)
sys.setdefaultencoding('utf-8')

class mysqlOperate(object):
     
    def __init__(self,host,user,passwd,database,port):
        try:
            self.dbserver = MySQLdb.connect(host=host,user=user,passwd=passwd,db=database,port=int(port),charset='utf8')
        except Exception,e:
            #db.close()
            error = 'ERROR:%s' % e
            raise Exception(error)
    def select(self,sql):
        cursor = self.dbserver.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        data_count = cursor.execute(sql)
        data = cursor.fetchall()
        #cursor.scroll(0,mode='absolute')
        # 获取MYSQL里面的数据字段名称
        #fields = cursor.description
        cursor.close()
        self.dbserver.close()
        return data
    

def jenkinsMysql(sql):
    host = '127.0.0.1'
    user = 'hsyt'
    passwd = 'mysql@1'
    database = 'hsyt'
    port = '3307'
    mysqlserver = mysqlOperate(host,user,passwd,database,port)
    data = mysqlserver.select(sql)
    return data

if __name__ == "__main__":
    sql = '''select nickname from svn_address_jobs_maps where install_job_name is not null and svn_address is not null GROUP BY nickname'''
    #sql = '''SELECT  belong_project as 'service_name',count(*) as 'deploy_count' from operation_log WHERE do_action='deploy' and op_environment='uat' and CREATE_TIME BETWEEN  DATE_ADD(now(), INTERVAL -1 DAY) and DATE_ADD(now(), INTERVAL 1 DAY) GROUP BY belong_project;'''

    data = jenkinsMysql(sql)
    print data
    #for i in  data:
    #    print i
     #   print i['nickname'],"---",i['svn_address']

