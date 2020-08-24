#encoding:utf-8
"""
oms api
"""

import os,sys
import hashlib
from settings import *
#from omsapp.models import *
from django.shortcuts import render

sys.path.append('../')

class OmsError(Exception):
    """
    self define exception
    自定义异常
    """
    pass


def page_not_found(request):
    return render(request, 'page_404.html')


def page_error(request):
    return render(request, 'page_500.html')


def permission_denied(request):
    return render(request, 'page_403.html')


def userlog_add(username,log_msg):
    """
    日志记录数据库模块
    """
    username and log_msg or userLog.objects.create(username=username,log_msg=log_msg)
        

def md5_crypt(string):
    '''
    md5非对称加密方法
    '''
    return hashlib.new("md5",string+SALT_KEY).hexdigest()





if __name__ == "__main__":
    print md5_crypt('7f82d27cbbb4c23d1a8fb2c10dffd95f1509502703.99')



