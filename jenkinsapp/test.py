


import os
import time

def child():
    print "getpid:%s" % os.getpid
    print "child"
    nu = 0 
    while True:
        nu += 10
        time.sleep(1)
        print nu
        if nu >= 100:
           #print nu
           break
    os._exit(0)



def main():
    newpid = os.fork()
    if newpid == 0:
        child()
    else:
        print "there is parent"



main()
