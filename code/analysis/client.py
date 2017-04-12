from multiprocessing import Queue
import os
import sys
import socket
from threading import Thread
import time
import shutil   

data = Queue()
def main():
        begin_time = time.time()

        t=Thread(target = printThread)
        t.start()
        
        t=Thread(target = client,args = {'Init'})
        t.start()

        print "Time Taken = ",time.time()-begin_time

def printThread():
    main_row = []
    leftover_data = ''

    while 1:
        try:
            row = data.get()
            
            row = leftover_data+row
            
            split_row = row.split('@')
            for r in split_row:
                if len(r)!=0:
                    print r.split('#')
            
            leftover_data = ''
            if row[-1] != '@':
                leftover_data = split_row(-1)
        except:
            print "Errorrrrr !!!!!"
            return


def client(*args):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        
        host = "116.73.34.9"
        port = 50001
        
        try :
                s.connect((host, port)) 

                s.settimeout(10.0)

                s.send(args[0])

                while True:
                        tm = s.recv(64)

                        print tm
                        if not tm:
                             break
                        data.put(tm)
                
                
                s.shutdown(socket.SHUT_RDWR)
                print "Socket Shutdown Complete !!"

        except socket.error as msg :
                print 'Connect failed. \nError Code : ' + str(msg)
                sys.exit(0)

if __name__=="__main__":
         main()

