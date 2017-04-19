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
	processedData = args[0]
	yawColumn = 6
	usColumn = 4

	while True:
		if int(formattedData.qsize()) == 0:
			continue
			firstRow = formattedData.get()
			break
	
	prevX = prevY = 0
	previousYaw = float(firstDataRow[yawColumn])
	previousDistance = float(firstDataRow[usColumn])
	
	while True:
		if int(formattedData.qsize()) == 0:
			continue

		dataList = formattedData.get()
		
		currentYaw = float(dataList[yawColumn])
		currentDistance = float(dataList[usColumn])

		distanceDiff = previousDistance-currentDistance

		if currentYaw-previousYaw > 35:
			previousDistance = currentDistance
			prevousYaw = currentYaw
			continue

		x = math.cos(math.radians(currentYaw))*distanceDiff + prevX
		y = math.sin(math.radians(currentYaw))*distanceDiff + prevY

		processedData.put([x,y])


#if __name__ == '__main__':
#	q = Queue()
#	processData('c',q )
