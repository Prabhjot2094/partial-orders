import math
import time
from threading import Thread
from multiprocessing import Process,Queue
import client
import random

formattedData = Queue()


def processData(*args):
        global formattedData
		
	try:
		if args[0]=='f':
			clientThread = Thread(name = "client", target=client.main, args=(args[0],args[1], formattedData, args[3]))
			processedData = args[2]
		else:
			clientThread = Thread(name = "client", target=client.main, args=(args[0], formattedData, args[2]))
			processedData = args[1]

		clientThread.setDaemon(True)
		clientThread.start()

	except Exception as e:
		print "Exception in DataProcessing OR Client spawned from DataProcessing ,",e
		raise Exception('In DataProcessing')

	coordinates(processedData)

def coordinates(*args):
	global formattedData
	processedData = args[0]
	yawColumn = 23
	usColumn = 3

	while True:
		if int(formattedData.qsize()) == 0:
			continue

		firstRow = formattedData.get()
		if int(firstRow[usColumn]) == 0:
			continue
		
		break
	
	x = y = 0
	previousYaw = float(firstRow[yawColumn])
	previousDistance = float(firstRow[usColumn])
	
	while True:
		if int(formattedData.qsize()) == 0:
			continue

		dataList = formattedData.get()
		
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
		
		distance = math.hypot(x - localX, y - localY)

		print "distance Diff = %f"%(distanceDiff)
		print "localX = %f, localY = %f, distance = %f"%(localX,localY,distance)
		#if distance > 7:
		#	continue

		x += localX
		y += localY

		previousDistance = currentDistance
		print "x = %f ,y = %f"%(x,y)
		processedData.put([x,y])


#if __name__ == '__main__':
#	q = Queue()
#	processData('c',q )
