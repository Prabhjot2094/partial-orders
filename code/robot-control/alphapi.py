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
import random

class AlphaPi(robot.Robot):
    x = 0.0
    y = 0.0
    dist_per_tick = 0.003745
    Dw = 8.9
    theta = 0
    leftEncoderTicks = 0
    rightEncoderTicks = 0
    lastX = lastY = 0.0

    turningFlag = False
    turnFlag = False
    prevUS = None

    interrupt = False

    def dataProcessor(self):
        return (self.processFromEncoders() or self.processFromSonars())

    def processFromSonars(self):
        obstaclePos = []

        # TBD
        # Add formulas to find out wall coordinates for three sensors
        # Experimentally set a limit for Sonar to start plotting when its close to wall

        for index in range(1, self.SONAR_NUM + 1):
            if self.sensorData[index] < 20 and self.sensorData[index] > 0:
                # Left Sonar
                if index == 1:
                    obstaclePos.append((1, 2))
                # Center Sonar
                elif index == 2:
                    obstaclePos.append((2, 3))
                # Right Sonar
                elif index == 3:
                    obstaclePos.append((4,5))
                return True
            else:
                return False
                
    def processFromEncoders(self):
        if self.leftEncoderTicks != self.sensorData[4] or self.rightEncoderTicks != self.sensorData[5]:
            deltaLeft = self.sensorData[4] - self.leftEncoderTicks
            deltaRight = self.sensorData[5] - self.rightEncoderTicks

            Dl = deltaLeft * self.dist_per_tick
            Dr = -1 * deltaRight * self.dist_per_tick 
            Dc = (Dl + Dr)/2
            
            self.theta = self.theta + (Dr - Dl)/self.Dw
            self.x = self.x + Dc * math.cos(self.theta)
            self.y = self.y + Dc * math.sin(self.theta)
            
            self.leftEncoderTicks = self.sensorData[4]
            self.rightEncoderTicks = self.sensorData[5]

            self.sensorData[-2] = [(self.x, self.y)]

            if abs(self.lastX - self.x) > 1 or abs(self.lastY - self.y) > 1:
                self.lastX = self.x
                self.lastY = self.y
                return True
            else:
                return False
        else: 
            return False

    def afterObstacleEvent(self, obstacle, speed, lock):
	# Left
	if obstacle < 0:
	    speedLeft = -speed
	    speedRight = speed
	    
	# Right
	else:
	    speedLeft = speed
	    speedRight = -speed
	self.turnFlag = True

	#self.writeMotorSpeeds(0, 0)
	#time.sleep(0.1)
	self.writeMotorSpeeds(speedLeft, speedRight)
	
	time.sleep(0.1 + 0.9*random.random())

	self.turnFlag = False

    def autopilot(self, type='sonar', speed=255):
	lock = threading.Lock()
        while True:
            if self.autopilotFlag:
                self.sensorData = self.getSensorData()

                if type == 'sonar':
                    obstacle = self.checkObstacle(self.sensorData)

                    if obstacle == 100:     # no obstacle
                        self.writeMotorSpeeds(speed, speed)
                        time.sleep(0.005)

                    elif obstacle < 0:      # obstacle towards left
                        self.afterObstacleEvent(obstacle, speed, lock)
                        
                    elif obstacle >= 0: # Obstacle towards right
                        self.afterObstacleEvent(obstacle, speed, lock)

            else:
                self.writeMotorSpeeds(0, 0)
                print "Autopilot Stopped"
                return

def main():
    global alphaPi
    alphaPi = AlphaPi(arduinoDataCount = 5, sonar_num = 3, ldr_num = 0, encoder_num = 2, dataReadInterval = 50, obstacleDistance = 12, verboseDataReporting = True)

    try:
	alphaPi.initialtime = time.time()

	try:
	    # Reset Encoders
	    alphaPi.writeMotorSpeeds(-1000, -1000)
	    dataReadThread = threading.Thread(target=alphaPi.readSensorData)

	    dataReadThread.setDaemon(True)
	    dataReadThread.start()

	except Exception as e:
	    print "Exception in dataReadThread " + str(e)
	    alphaPi.shutdown()

	alphaPi.drive('autopilot-sonar', 255, True)

	#while True:
	    #time.sleep(0.01)

    except KeyboardInterrupt:
	alphaPi.shutdown()

    except Exception as e:
	print "Exception in main " + str(e)
	alphaPi.shutdown()
	raise

main()

