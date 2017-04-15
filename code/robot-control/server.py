'''
    Simple socket server using threads
'''
#import lambda-master as lm
import time
import lambdaMasterEMU as lm
import socket
import sys
from threading import Thread
import threading
import os


def main():
    
    HOST = '0.0.0.0'
    PORT = 50000

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
    dataThread = Thread(target=lm.getData)
    dataThread.start()
    while 1:
        i+=1
        conn, addr = s.accept()
        
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        
        t=Thread(target = clientThread,args = (conn,))
        t.start()
        

def clientThread(conn):
    # s = SEND A SINGLE RECORD
    # f = SEND RECORDS CONTINUOUSLY AT FREQUENCY f
    # c = SEND RECORDS CONTINUOUSLY AFAP

    try:
        initCharacter = conn.recv(128)
        print str(initCharacter)
        print 'c'

        if initCharacter == "s":
            while lm.sensorDataReady is 0:
                continue
            
            data = '@'+str(lm.sensorData)+'@'            
            conn.send(data)
            conn.close()
            
            return

        elif initCharacter == "f":
            frequency = conn.recv(128)

            while lm.sensorDataReady is 0:
                continue
            prev_timestamp = float(lm.sensordata[0])
            
            while 1:
                current_timestamp = float(lm.sensordata[0])
                if (current_timestamp-prev_timestamp) > frequency:
                    prev_timestamp = current_timestamp
                    while lm.sensorDataReady is 0:
                        continue
                    data = '@'+str(lm.sensorData)+'@'
                    conn.send(data);

        elif str(initCharacter)=="c":
            print "In the shit"
            prevData = ""
            while 1:
                while lm.sensorDataReady is 0:
                    continue
                data = '@'+str(lm.sensorData)+'@'
                if prevData != data:
                    conn.send(data)
                prevData = data
        else:
            print "No match"

    except socket.error as msg:
        conn.close()    
        print 'Connect failed. \nError Code : ' + str(msg[0]) + ' \nMessage :' + msg[1]
        return

if __name__=="__main__":
    main()


