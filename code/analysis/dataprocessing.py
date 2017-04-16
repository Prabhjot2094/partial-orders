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
		print "Exception in client spawned from DataProcessing thread , "+str(e)
		raise Exception('Client thread encountered an error')

	while True:
	    if int(formattedData.qsize()) == 0:
	        #print "Continuing"
	        continue
            tmp = formattedData.get()
            args[-1].put(tmp[:3])



#if __name__ == '__main__':
#	q = Queue()
#	processData('c',q )
