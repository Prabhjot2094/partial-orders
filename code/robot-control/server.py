import lambdamaster as lm
import time
#import lambdaMasterEMU as lm
import socket
import sys
from threading import Thread
import threading
import os


threadActiveCount = 0
def main():
    global threadActiveCount
    try:
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
         
        try:
            lm.drive('forward',255,True)
            #dataThread = Thread(target=lm.getData)
            #dataThread.setDaemon(True)
            #dataThread.start()
        except Exception as e:
            print "Exception in Sensor Data thread, ",e
            sys.exit(0)
        
        i=0
        while 1:
            i+=1
            conn, addr = s.accept()
            
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
           
            try:
                t=Thread(target = clientThread,args = (conn,))
                t.setDaemon(True)
                t.start()
                threadActiveCount += 1
            
            except Exception as e:
                print "Exception in client connection thread, ",e
                sys.exit(0)
    
    except KeyboardInterrupt:
        lm.drive('halt')
        

def clientThread(conn):
    # s = SEND A SINGLE RECORD
    # f = SEND RECORDS CONTINUOUSLY AT FREQUENCY f
    # c = SEND RECORDS CONTINUOUSLY AFAP

    global threadActiveCount
    try:
        initCharacter = conn.recv(1)
        print str(initCharacter)

        if initCharacter == "s":
            data = '@'+str(lm.getSensorData())+'@'
            conn.send(data)
            conn.close()
            return

        elif initCharacter == "f":
            frequency = float(conn.recv(38))
            while 1:
                data = '@'+str(lm.getSensorData())+'@'
                conn.send(data);
                time.sleep(frequency)

        elif str(initCharacter)=="c":
            while 1:
                data = '@'+str(lm.getSensorData())+'@'
                conn.send(data)
                print data

        else:
            print "No match"

    except socket.error as msg:
        threadActiveCount -= 1
        if threadActiveCount is 0:
            lm.halt()

        conn.close()    
        print 'Connect failed. \nError Code : ' + str(msg[0]) + ' \nMessage :' + msg[1]
        return
		

if __name__=="__main__":
    main()
