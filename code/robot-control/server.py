import time
import alphapi as lm
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
         
        print "Driving"
#        lm.drive("autopilot-sonar",255,False)
        
        i=0
        while 1:
            i+=1
            conn, addr = s.accept()
            
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
           
            try:
                t=Thread(target = clientThread,args = (conn,))
                #t.setDaemon(True)
                t.start()
            
                #threadActiveCount += 1
            except Exception as e:
                print "Exception in client connection thread, ",e
                sys.exit(0)
    
    except KeyboardInterrupt:
        s.close()
        lm.alphaPi.drive('halt')
        time.sleep(2)

def clientThread(conn):
    # s = SEND A SINGLE RECORD
    # f = SEND RECORDS CONTINUOUSLY AT FREQUENCY f
    # c = SEND RECORDS CONTINUOUSLY AFAP

    global threadActiveCount
    try:
        threadActiveCount += 1
        #if threadActiveCount == 1:
        #    print "Autopilot Called"
        #    lm.drive("autopilot-sonar",255,False)
        initCharacter = conn.recv(1)
        print str(initCharacter)

        if initCharacter == "s":
            while int(lm.sensorDataQueue.qsize()) == 0:
                continue
            data = '@'+str(lm.sensorDataQueue.get())+'@'
            conn.send(data)
            conn.close()
            return

        elif initCharacter == "f":
            frequency = float(conn.recv(38))
            while 1:
                while int(lm.sensorDataQueue.qsize()) == 0:
                    continue
                data = '@'+str(lm.sensorDataQueue.get())+'@'
                conn.send(data);
                time.sleep(frequency)

        elif str(initCharacter)=="c":
            print "Sending Continuous Data"
            while 1:
                while int(lm.alphaPi.sensorDataQueue.qsize()) == 0:
                    time.sleep(0.05)
                
                data_array = lm.alphaPi.sensorDataQueue.get()
                #print data_array[-2]
                data = '@'+str(data_array)+'@'
                conn.send(data)
                time.sleep(0.05)
        else:
            print "No match"

    except socket.error as msg:
        threadActiveCount -= 1
        if threadActiveCount is 0:
            lm.alphaPi.drive('stop')

        conn.close()    
        print 'Connect failed. \nError Code : ' + str(msg[0]) + ' \nMessage :' + msg[1]
        return
		

if __name__=="__main__":
    main()
