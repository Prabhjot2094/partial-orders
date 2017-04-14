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
    # s = SEND A SINGLE RECORD
    # f = SEND RECORDS CONTINUOUSLY AT FREQUENCY f
    # c = SEND RECORDS CONTINUOUSLY AFAP

    try:
        initCharacter = conn.recv(128)

        if initCharacter is 's':
            conn.send(latest_record)
            conn.close()
            return

        elif initCharacter is 'f':
            frequency = conn.recv(128)
            prev_timestamp = float(latest_record[0])
            
            while 1:
                current_timestamp = float(latest_record[0])
                if (current_timestamp-prev_timestamp) > frequency:
                    prev_timestamp = current_timestamp
                    conn.send(latest_record);

        elif initCharacter is 'c':
            while 1:
                conn.send(latest_record)


        if rows_requested is 1:
        else: 

    except socket.error as msg:
        conn.close()    
        print 'Connect failed. \nError Code : ' + str(msg[0]) + ' \nMessage :' + msg[1]
        return

if __name__=="__main__":
    main()


