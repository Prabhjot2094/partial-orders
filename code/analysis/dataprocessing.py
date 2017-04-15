import time
from threading import Thread
from multiprocessing import Queue
import client
import random

processedData = Queue()

def initQueue():
	for i in range(1,100):
		l = [random.randint(1,100) for i in range(3)]
		formattedData.put(l)

	for i in range(formattedData.qsize()):
		processedData.put(formattedData.get())

	print "Complete"

def processData():

	clientThread = Thread(target=client.main, args=('c'))
	clientThread.start()

	while True:
	    if int(client.formattedData.qsize()) == 0:
	        continue

            tmp = client.formattedData.get()
            processedData.put(tmp[:3])

	print "Complete"


if __name__ == '__main__':
	processData()
