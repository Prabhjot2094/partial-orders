import time
import random

sensorData = [0] * 10
sensorDataReady = 1

def getData():
        global sensorDataReady
	while 1:
	        sensorDataReady = 1
		for i in range(10):
			sensorData[i] = random.randint(1,100)
		sensorDataReady = 1
