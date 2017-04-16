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

def main(*params):
	begin_time = time.time()

	try:
		t=Thread(target = printThread, args = (params[-1],))
		t.setDaemon(True)
		t.start()
	
		if len(params)==3:
		    t=Thread(target = client,args = (params[1],params[0],)) # OR {1,freq}
		else:
		    t=Thread(target = client,args = (params[0],)) # OR {1,freq}
		t.setDaemon(True)
		t.start()
	except Exception as e:
		print "Exception in client thread, "+str(e)
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
            print "Errorrrrr !!!!!"
            return


def client(*args):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        
        host = "192.168.1.25"
        port = 50001
        
        try :
                s.connect((host, port)) 

                s.settimeout(10.0)

                print args
                s.send(args[0])
                if args[0]=='f':
                    s.send(args[1])

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
#q = Queue()
#main('c',q)
