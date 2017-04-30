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
    dist_per_tick = 0.0366519
    Dw = 9.2
    theta_old = 0

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
        self.processFromEncoders()

    def processFromEncoders(self): 
	global x_old,y_old,theta_old
	global dist_per_tick

	Dw = 9.2

	if abs(self.sensorData[self.SONAR_NUM + 1]) > 500:
	    return 

	encoderLeft = self.sensorData[self.SONAR_NUM + 1]
	encoderRight = self.sensorData[self.SONAR_NUM + 2]

	Dl = encoderLeft * self.dist_per_tick;
	Dr = encoderRight * self.dist_per_tick;
	Dc = (Dl + Dr)/2.0;

	theta_inst = (Dr - Dl)/Dw;

	theta_new = self.theta_old + (Dr - Dl)/Dw;
	x_new = self.x_old + Dc*math.cos(theta_new);
	y_new = self.y_old + Dc*math.sin(theta_new);

	wall2_x = x_new + self.sensorData[2]*math.cos(theta_inst)
	wall2_x = x_new + self.sensorData[2]*math.cos(theta_inst)

	if abs(self.x_old - x_new) > 10 or abs(self.y_old - y_new) > 10:
	    return False

	if x_new != self.x_old or y_new != self.y_old:
	    self.sensorData[-2] = [(x_new, y_new)]
	    #print sensorData
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


	self.writeMotorSpeeds(speedLeft, speedRight)
	time.sleep(0.7)

	lock.acquire()
	self.dataProcessor()
	lock.release()

	time.sleep(0.2)

 
    def autopilot(self, type='sonar', speed=255):
	lock = threading.Lock()
        while True:
            if self.autopilotFlag:
                self.sensorData = self.getSensorData()

                if not self.VERBOSE_DATA_REPORTING:
                    self.dataProcessor()
                    self.sensorDataQueue.put(self.sensorData)

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
    alphaPi = AlphaPi()
    try:
	alphaPi.initialtime = time.time()

	try:
	    dataReadThread = threading.Thread(target=alphaPi.readSensorData)
	    dataReadThread.setDaemon(True)
	    dataReadThread.start()
	except Exception as e:
	    print "Exception in dataReadThread " + str(e)
	    lambdaPi.shutdown()

	alphaPi.drive('autopilot-sonar', 255, False)
	while True:
	    print alphaPi.sensorData
	    time.sleep(0.01)

    except KeyboardInterrupt:
	alphaPi.shutdown()

    except Exception as e:
	print "Exception in main " + str(e)
	alphaPi.shutdown()
	raise

main()

