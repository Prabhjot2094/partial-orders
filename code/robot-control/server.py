import lambdamaster as lm
import time
#import lambdaMasterEMU as lm
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
     
    try:
    	lm.drive('forward',127,True)
        #dataThread = Thread(target=lm.getData)
        #dataThread.setDaemon(True)
        #dataThread.start()
    except Exception as e:
        print "Exception in Sensor Data thread, "+e
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
	
        except Exception as e:
            print "Exception in client connection thread, "+e
            sys.exit(0)
        

def clientThread(conn):
    # s = SEND A SINGLE RECORD
    # f = SEND RECORDS CONTINUOUSLY AT FREQUENCY f
    # c = SEND RECORDS CONTINUOUSLY AFAP

    try:
        initCharacter = conn.recv(1)
        print str(initCharacter)

        if initCharacter == "s":
            if lm.sensorDataReady:
                data = '@'+str(lm.sensorData)+'@'            
                conn.send(data)
                conn.close()
            return

        elif initCharacter == "f":
            frequency = float(conn.recv(38))
            while 1:
                if lm.sensorDataReady:
                    data = '@'+str(lm.sensorData)+'@'
                    conn.send(data);
                    time.sleep(frequency)
                    while lm.sensorDataReady:
                        continue

        elif str(initCharacter)=="c":
            prevData = ""
            while 1:
            	print lm.sensorDataReady
                if lm.sensorDataReady:
                    data = '@'+str(lm.sensorData)+'@'
                    print data
                    conn.send(data)
                    while lm.sensorDataReady:
                        continue

        else:
            print "No match"

    except socket.error as msg:
        conn.close()    
        print 'Connect failed. \nError Code : ' + str(msg[0]) + ' \nMessage :' + msg[1]
        return
	except KeyboardInterrupt:
		lm.halt()
		

if __name__=="__main__":
    main()


