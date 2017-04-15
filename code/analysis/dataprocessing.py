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

def processData(*args):
	try:
		if args[0]=='f':
			clientThread = Thread(name = "client", target=client.main, args=(args[1],args[0]))
		else:
			clientThread = Thread(name = "client", target=client.main, args=(args[0]))

		clientThread.setDaemon(True)
		clientThread.start()
	except Exception as e:
		print "Exception in client spawned from DataProcessing thread , "+str(e)
		raise Exception('Client thread encountered an error')

	while True:
	    if int(client.formattedData.qsize()) == 0:
	        continue

            tmp = client.formattedData.get()
            processedData.put(tmp[:3])



#if __name__ == '__main__':
#	processData()
