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

    x = 0.0
    y = 0.0

    wall2_x_old = 0.0
    wall2_y_old = 0.0

    us2 = 0

    prevX = prevY = None
    turningFlag = False
    turnFlag = False
    prevUS = None

    interrupt = False

    def getYawReference(self, currentYaw):
	currentYaw -= self.referenceYaw
	if currentYaw > 180:
	    currentYaw -= 360
	elif currentYaw < -180:
	    currentYaw += 360
	return currentYaw

    def dataProcessor(self):
        return self.processFromEncoders()

    def processFromEncoders(self): 
	Dw = 9.2

	if abs(self.sensorData[self.SONAR_NUM + 1]) > 500:
	    return 

	encoderLeft = self.sensorData[self.SONAR_NUM + 1]
	encoderRight = -self.sensorData[self.SONAR_NUM + 2]

        self.x  = self.x  + encoderLeft
        self.y = self.y + encoderRight
        print self.x, self.y 
        
	Dl = encoderLeft * self.dist_per_tick;
	Dr = encoderRight * self.dist_per_tick;
	Dc = (Dl + Dr)/2.0;

	theta_inst = (Dr - Dl)/Dw;

	theta_new = self.theta_old + (Dr - Dl)/Dw;
	x_new = self.x_old + Dc*math.cos(theta_new);
	y_new = self.y_old + Dc*math.sin(theta_new);

	us2 = self.sensorData[2]
	wall2_x = x_new + us2*math.cos(theta_new)
	wall2_y = y_new + us2*math.sin(theta_new)

	if abs(self.x_old - x_new) > 10 or abs(self.y_old - y_new) > 10:
	    return False

	if (x_new != self.x_old or y_new != self.y_old) and not self.turnFlag:
	    #print x_new, y_new
            if (abs(self.us2 - us2) < 20 and us2 > 0 and us2 < 20):
                #self.sensorData[-1] = [(wall2_x, wall2_y)]
                self.us2 = us2
            else:
                self.us2 = us2

	    self.sensorData[-2] = [(x_new, y_new)]

	    self.x_old = x_new;
	    self.y_old = y_new;
	    self.theta_old = theta_new;

	    return True

	else:
	    self.x_old = x_new;
	    self.y_old = y_new;
	    self.theta_old = theta_new;

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
    alphaPi = AlphaPi(arduinoDataCount = 5, sonar_num = 3, dataReadInterval = 50, obstacleDistance = 10, verboseDataReporting = True)

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

