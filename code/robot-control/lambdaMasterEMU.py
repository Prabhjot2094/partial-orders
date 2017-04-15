import random

sensorData = [0] * 10
sensorDataReady = 1

def getData():
	while 1:
		for i in range(10):
			sensorData[i] = random.randint(1,100)
