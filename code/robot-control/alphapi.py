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

class AlphaPi(robot.Robot):

    x_old = 0.0
    y_old = 0.0
    dist_per_tick = 0.003745
    Dw = 9.2
    theta_old = 0

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
        x = sensorData[self.SONAR_NUM + 0]
        y = sensorData[self.SONAR_NUM + 1]
        theta = sensorData[self.SONAR_NUM + 2]

        # Plot position if x or y or angle change and robot is not turning
        if (x != self.x or y != self.y or theta != self.theta) and (not self.turnFlag):
            sensorData[-2] = [(x, y)]
            self.x = x
            self.y = y
            self.theta = theta
            return True

        else:
            self.x = x
            self.y = y
            self.theta = theta
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

	self.writeMotorSpeeds(0, 0)
	time.sleep(0.1)
	self.writeMotorSpeeds(speedLeft, speedRight)
	time.sleep(1)

	self.turnFlag = False

    def autopilot(self, type='sonar', speed=255):
	lock = threading.Lock()
        while True:
            if self.autopilotFlag:
                self.sensorData = self.getSensorData()

                if type == 'sonar':
                    self.writeMotorSpeeds(speed, speed)

                    obstacle = self.checkObstacle(self.sensorData)

                    if obstacle == 100:     # no obstacle
                        self.writeMotorSpeeds(speed, speed)
                        time.sleep(0.005)

                    elif obstacle < 0:      # obstacle towards left
                        print 'obstacle left'
                        self.afterObstacleEvent(obstacle, speed, lock)
                        
                    elif obstacle >= 0: # Obstacle towards right
                        print 'obstacle right'
                        self.afterObstacleEvent(obstacle, speed, lock)

            else:
                self.writeMotorSpeeds(0, 0)
                print "Autopilot Stopped"
                return

def main():

    global alphaPi
    alphaPi = AlphaPi(arduinoDataCount = 6, sonar_num = 3, dataReadInterval = 50, obstacleDistance = 15, verboseDataReporting = True)

    try:
	alphaPi.initialtime = time.time()

	try:
	    # Reset Encoders
	    alphaPi.writeMotorSpeeds(-100, -100)
	    dataReadThread = threading.Thread(target=alphaPi.readSensorData)

	    dataReadThread.setDaemon(True)
	    dataReadThread.start()
	except Exception as e:
	    print "Exception in dataReadThread " + str(e)
	    lambdaPi.shutdown()

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

