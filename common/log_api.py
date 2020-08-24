#!/usr/bin/python
#ecoding:utf-8
'''
通用日志输出模块
'''
import os
import logging
import logging.handlers 
from oms.settings import LOG_LEVEL,LOG_DIR


def logset(level,log_file='oms.log'):
    log_file = "oms.log"
    log_dir = LOG_DIR
    log_filename = os.path.join(log_dir,log_file)
    #logging.debug("Send mail "+subject+" to "+to_list)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print log_dir,"is exists mkdir success"
    if not os.path.isfile(log_filename):
        os.system(r'touch %s' % log_filename)
        print log_filename,"is exsits and touch success"

    log_level_total = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARN': logging.WARN, 'ERROR': logging.ERROR,'CRITICAL': logging.CRITICAL,
                       'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN, 'error': logging.ERROR,'critical': logging.CRITICAL}
    log_format = logging.Formatter('[%(asctime)s] [%(levelname)s]-[%(pathname)s:%(lineno)s]-[function:%(funcName)s]-[%(threadName)s]-%(message)s')
    logger = logging.getLogger('oms')
    logger.setLevel(log_level_total.get(level,logging.DEBUG))
    #记录到日志文件中的handler
    fh = logging.FileHandler(log_filename)
    fh.setLevel(logging.DEBUG)
    #输出到面板的Handler
    #ch = logging.StreamHandler()
    #ch.setLevel(logging.DEBUG)
    #定义Handler输出格式
    fh.setFormatter(log_format)
    #ch.setFormatter(log_format)
    #给logger添加handler
    logger.addHandler(fh)
    #logger.addHandler(ch)
    
    return logger

logger = logset(LOG_LEVEL) 
if __name__ == "__main__":
    #logset()
    logger.debug("this is debug log")
    logger.info("this is info log")
    logger.error("this is error log")
