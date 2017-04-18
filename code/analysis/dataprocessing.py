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
			clientThread = Thread(name = "client", target=client.main, args=(args[1],args[0], formattedData,))
		else:
			clientThread = Thread(name = "client", target=client.main, args=(args[0], formattedData,))

		clientThread.setDaemon(True)
		clientThread.start()
	except Exception as e:
		print "Exception in DataProcessing OR Client spawned from DataProcessing , "+str(e)
		raise Exception('In DataProcessing')

	while True:
	    if int(formattedData.qsize()) == 0:
	        #print "Continuing"
	        continue
            tmp = formattedData.get()
            args[-1].put(tmp[:3])

def coordinates(*args):
	#filePath-----Path of the file whose data is to be processed
    with open(filePath, 'rb') as inputFile, open('../../data/transformations/sameValues/' + getFileName() + \
            '_sameValues_.csv', 'wb') as outputFile:
        
        spamInput = csv.reader(inputFile, delimiter=',')
        spamOutput = csv.writer(outputFile, delimiter=',')

        columnLabels = next(spamInput)

        try:
           yawColumn = columnLabels.index('YAW')
           usColumn = columnLabels.index('US_3')
        except:
           return "Unknown column"

        firstDataRow = next(spamInput)

        prevX = prevY = 0
        previousYaw = float(firstDataRow[yawColumn])
        previousDistance = float(firstDataRow[usColumn])
        
        for row in spamInput:
            currentYaw = float(row[yawColumn])
            currentDistance = float(row[usColumn])

            distanceDiff = previousDistance-currentDistance

            if currentYaw-previousYaw > 35:
                previousDistance = currentDistance
                prevousYaw = currentYaw
                continue

            x = math.cos(math.radians(currentYaw))*distanceDiff + prevX
            y = math.sin(math.radians(currentYaw))*distanceDiff + prevY

            spamOutput.writerow([row[0],row[yawColumn],row[usColumn],x,y])


#if __name__ == '__main__':
#	q = Queue()
#	processData('c',q )
