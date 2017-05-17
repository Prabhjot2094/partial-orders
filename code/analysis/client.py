import ast
from multiprocessing import Queue
import os
import sys
import socket
from threading import Thread
import threading
import time
import shutil   

_HOST = "alphapi.local"
#_HOST = "192.168.1.26"

rawData = Queue()

def main(**kwargs):

    begin_time = time.time()

    print threading.activeCount()
    try:
        formatDataThread = Thread(target = printThread, args = (kwargs['processedData'],))
        clientThread = Thread(target = client,kwargs = {'ip':kwargs['ip']})
        print "Thread Created"
        
        formatDataThread.setDaemon(True)
        clientThread.setDaemon(True)

        formatDataThread.start()
        clientThread.start()

    except Exception as e:
        print e
        raise Exception('Client thread encountered an error')

    print "Time Taken = ",time.time()-begin_time
    while 1:
        continue

def printThread(formattedData):
    main_row = []
    leftover_data = ''

    while 1:
        try:
            row = rawData.get()

            row = leftover_data+row

            split_row = row.split('@')
            for r in split_row:
                if len(r) is 0 or r[-1] is not ']':
                    continue
                l = ast.literal_eval(r)
                formattedData.put(l)
            
            leftover_data = ''

            if row[-1] != '@':
                leftover_data = split_row[-1]
        
        except Exception as e:
        	print e
        	print "Error"
        	return
        	#printThread(formattedData)


def client(**kwargs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        
    host = kwargs['ip']
    port = 50001

    try :
        s.connect((host, port)) 

        s.settimeout(30.0)

        print kwargs
        s.send("c")
        
        while True:
            tm = s.recv(1024)

            if not tm:
                break
            rawData.put(tm)

        s.shutdown(socket.SHUT_RDWR)
        print "Socket Shutdown Complete !!"
        sys.exit(0)
        return

    except socket.error as msg :
        print 'Connect failed. \nError Code : ' + str(msg)
        return

#if __name__=="__main__":
#    q = Queue()
#    main(ip = 'alphapi.local',processedData=q)
