import math
import time
from threading import Thread
from multiprocessing import Process,Queue
import client
import random

class processData():

    def __init__(self,**kwargs):
        self.formattedData = Queue()

        try:
            clientThread = Thread(name = "client", target=client.main, kwargs={'processedData':kwargs['processedData'],'ip': kwargs['ip']})

            clientThread.setDaemon(True)
            clientThread.start()

            while 1:
                pass

        except Exception as e:
            print "Exception in DataProcessing OR Client spawned from DataProcessing ,",e
            #raise Exception('In DataProcessing')

        #self.coordinates()

    def coordinates(self):
        yawColumn = 23
        usColumn = 3

        while True:
            if int(self.formattedData.qsize()) == 0:
                continue
            
            firstRow = self.formattedData.get()

            if int(firstRow[usColumn]) == 0:
                continue

            break

        x = y = 0
        previousYaw = float(firstRow[yawColumn])
        previousDistance = float(firstRow[usColumn])

        while True:
            if int(self.formattedData.qsize()) == 0:
                continue

            dataList = self.formattedData.get()

            currentYaw = float(dataList[yawColumn])
            currentDistance = float(dataList[usColumn])

            if currentDistance == 0:
                continue
            
            distanceDiff = previousDistance-currentDistance

            if currentYaw-previousYaw > 35:
                previousDistance = currentDistance
                prevousYaw = currentYaw
                continue

            localX = math.cos(math.radians(currentYaw))*distanceDiff
            localY = math.sin(math.radians(currentYaw))*distanceDiff

            distance = math.hypot(x-localX, y-localY)

            x += localX
            y += localY

            previousDistance = currentDistance
            
            self.processedData.put([x,y,0])


#if __name__ == '__main__':
#	q = Queue()
#        processData(ip = 'alphapi.local',processedData=q)
