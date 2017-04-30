import math
from multiprocessing import Queue
import csv
import os
import smbus
import time
import threading
import serial
import sys
import robot

class LambdaPi(robot.Robot):
    
    prevX,prevY = None,None
    x,y = 0,0
    prevUS = [None,None]
    turningFlag = False
    turnFlag = False
    referenceYaw = None
    interrupt = False

    def getYawReference(self, currentYaw):
        currentYaw -= self.referenceYaw
        if currentYaw > 180:
            currentYaw -= 360
        elif currentYaw < -180:
            currentYaw += 360
        return currentYaw
    
    def processFromSonar(self):
        if self.prevX is None and self.prevY is None:
            self.prevUS[0] = float(self.sensorData[self.US_INDEX])
            if self.prevUS[0] == 0:
                self.prevUS = [None,None]
                self.sensorData[-2] = [(0,0)]
                return
            
            self.referenceYaw = float(self.sensorData[self.YAW_INDEX])

            self.sensorData[-2] = [(0,0)]
            self.prevX = self.prevY = 0
            return
        
        if self.turnFlag is True and self.turningFlag is False:
            self.turningFlag = True
            self.sensorData[-2] = ["Turn Start"]
            #print "turn = %s, turning = %s"%(self.turnFlag,self.turningFlag)
            #print self.prevUS
            #print self.sensorData
            return

        elif self.turnFlag is False and self.turningFlag is True:
            self.turningFlag = False
            self.sensorData[-2] = ["Turn End"]
            self.prevUS[1] = None
            self.prevUS[0] = float(self.sensorData[self.US_INDEX])
            #print "turn = %s, turning = %s"%(self.turnFlag,self.turningFlag)
            #print self.prevUS
            #print self.sensorData
            #currentYaw = getYawReference(float(self.sensorData[self.YAW_INDEX]))
            #x -= math.cos(math.radians(currentYaw))*ROBOT_SPEED*0.7
            #y -= math.sin(math.radians(currentYaw))*ROBOT_SPEED*0.7
            self.autopilotStartTime = time.time()
            return

        currentYaw = float(self.sensorData[self.YAW_INDEX])
        currentYaw = self.getYawReference(currentYaw)
        
        distance = self.ROBOT_SPEED*(time.time()-self.autopilotStartTime)
        self.autopilotStartTime = time.time()

        localX = math.cos(math.radians(currentYaw))*distance
        localY = math.sin(math.radians(currentYaw))*distance

        self.x+=localX
        self.y+=localY
        
        self.sensorData[-1] = [(self.x,self.y)]
        #print currentYaw
        #print self.sensorData[-1]

        currentDistance = float(self.sensorData[self.US_INDEX])

        distanceDiff = self.prevUS[0] - currentDistance
        
        if currentDistance == 0:
            self.sensorData[-2] = [(self.prevX,self.prevY)]
            return
       
        if distanceDiff > self.MAX_DISTANCE_DIFF or distanceDiff < 0:
            if self.prevUS[1] == None:
                self.sensorData[-2] = [(self.prevX,self.prevY)]
                self.prevUS[1] = self.prevUS[0]
                self.prevUS[0] = currentDistance
                return
            else:
                correctUS = [prev_us-currentDistance if prev_us>currentDistance else 999 for prev_us in self.prevUS]
                distanceDiff = min([i for i in correctUS])
                pos = [prev_us for prev_us in correctUS].index(distanceDiff)

                if distanceDiff > self.MAX_DISTANCE_DIFF :
                    self.sensorData[-2] = [(self.prevX,self.prevY)]
                    self.prevUS[1] = self.prevUS[0]
                    self.prevUS[0] = currentDistance

                    return
                self.prevUS[1] = self.prevUS[pos]
                self.prevUS[0] = currentDistance
        
        localX = math.cos(math.radians(currentYaw))*distanceDiff
        localY = math.sin(math.radians(currentYaw))*distanceDiff

        '''
        tempX = self.prevX + localX
        tempY = self.prevY + localY
        distance = math.hypot(tempX-self.prevX, tempY-self.prevY)
        if distance > MAX_DISTANCE_DIFF :
            self.sensorData[-2] = self.prevX
            self.sensorData[-1] = self.prevY
            return
        '''

        self.prevX += localX
        self.prevY += localY

        self.sensorData[-2] = [(self.prevX,self.prevY)]
        self.prevUS[1] = self.prevUS[0]
        self.prevUS[0] = currentDistance

    
    def autopilot(self, type='sonar', speed=255):
        lock = threading.Lock()
        while True:
            if self.autopilotFlag:
                self.sensorData = self.getSensorData()

                if not self.VERBOSE_DATA_REPORTING:
                    self.dataProcessor()
                    self.sensorDataQueue.put(self.sensorData)

                if type == 'sonar':
                    obstacleArray = []
                    obstacle = self.checkObstacle(self.sensorData, obstacleArray)
                    
                    if obstacle == 100:     # no obstacle
                        self.writeMotorSpeeds(speed, speed)
                        time.sleep(0.01)
                    elif obstacle < 0:      # obstacle towards left
                        self.turnFlag = True
                        self.writeMotorSpeeds(speed, -speed)
                        
                        lock.acquire()
                        self.dataProcessor()
                        self.sensorDataQueue.put(self.sensorData)
                        lock.release()
                        
                        time.sleep(.700)
                        self.writeMotorSpeeds(0, 0)
                        self.turnFlag = False
                    elif obstacle >= 0:     # obstacle towards right or in front
                        self.turnFlag = True
                        
                        lock.acquire()
                        self.dataProcessor()
                        self.sensorDataQueue.put(self.sensorData)
                        lock.release()
                        
                        self.writeMotorSpeeds(-speed, speed)
                        time.sleep(.700)
                        self.writeMotorSpeeds(0, 0)
                        self.turnFlag = False
            else:
                self.writeMotorSpeeds(0, 0)
                print "Autopilot Stopped"
                return

def main():
    lambdaPi = LambdaPi()
    try:
        lambdaPi.initialtime = time.time()

        try:
            dataReadThread = threading.Thread(target=lambdaPi.readSensorData)
            dataReadThread.setDaemon(True)
            dataReadThread.start()
        except Exception as e:
            print "Exception in dataReadThread " + str(e)
            lambdaPi.shutdown()

        lambdaPi.drive('autopilot-sonar', 255, False)
        while True:
            time.sleep(0.01)

    except KeyboardInterrupt:
       lambdaPi.shutdown()

    except Exception as e:
        print "Exception in main " + str(e)
        lambdaPi.shutdown()
        raise

main()
