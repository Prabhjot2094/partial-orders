import ast
from multiprocessing import Queue
import os
import sys
import socket
from threading import Thread
import time
import shutil   

rawData = Queue()
formattedData = Queue()

def main(requestParams):
	begin_time = time.time()

	t=Thread(target = printThread)
	t.start()
	
	t=Thread(target = client,args = {requestParams}) # OR {1,freq}
	t.start()

	print "Time Taken = ",time.time()-begin_time

def printThread():
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
            print "Errorrrrr !!!!!"
            return


def client(*args):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        
        host = "0.0.0.0"
        port = 50000
        
        try :
                s.connect((host, port)) 

                s.settimeout(10.0)

                s.send(args[0])

                while True:
                        tm = s.recv(64)

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
#       #main('c')
