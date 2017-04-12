'''
    Simple socket server using threads
'''
import socket
import sys
from threading import Thread
import threading
import os


def main():
    HOST = '0.0.0.0'
    PORT = 50001

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'Socket created'

    try:
        s.bind((HOST, PORT))
        print 'Socket bind complete'
    except socket.error as msg:
        print 'Bind failed. \nError Code : ' + str(msg[0]) + ' \nMessage :' + msg[1]
        sys.exit(0)

    s.listen(0)
    print 'Socket now listening'
     
    i=0
    while 1:
        i+=1
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        t=Thread(target = clientThread,args = (conn,))
        t.start()
        print threading.activeCount();


def clientThread(conn):

    try:
        init = conn.recv(512)
        print init
        
        #while 1:
        conn.send("@1,2,3#a,b,c#4,5,6@1,2,3#a,b,c#4,5,6@1,2,3#a,b,c#4,5,6@");

    except socket.error as msg:
        conn.close()    
        print 'Connect failed. \nError Code : ' + str(msg[0]) + ' \nMessage :' + msg[1]
        return

if __name__=="__main__":
    main()


