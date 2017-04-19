import time
import random

sensorData = [0] * 10
sensorDataReady = False

def getSensorData():
	while not sensorDataReady:
		pass
	return sensorData

def getData():
        global sensorDataReady
	while 1:
	        sensorDataReady = False
		for i in range(10):
			sensorData[i] = random.randint(1,100)
		time.sleep(0.006)
		sensorDataReady = True
		time.sleep(0.004)
