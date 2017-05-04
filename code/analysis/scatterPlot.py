import sys
from threading import Thread
from multiprocessing import Process,Queue
import dataprocessing as data
import random
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time

class scatter_plot:

    xMax = 100
    yMax = 100
    xMin = -100
    yMin = -100
    def __init__(self,processedData):
        self.processedData = processedData
        app = QtGui.QApplication([])
        mw = QtGui.QMainWindow()

        self.p = pg.plot()
        self.p.setYRange(self.yMin,self.yMax,padding=0)
        self.p.setXRange(self.xMin,self.xMax,padding=0)

        self.ptr = 0
        self.prev = [0,0]

        self.curve = pg.ScatterPlotItem(pen='r',symbol='o')
        self.p.addItem(self.curve)
        
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(0)

        QtGui.QApplication.instance().exec_()
	
    def update(self):
        if int(self.processedData.qsize()) is 0:
            return
        
        dataRow = self.processedData.get()
        pos,wall = dataRow[-2], dataRow[-1]

        print pos
        if self.prev == dataRow:
            self.prev = dataRow
            return

        if type(pos) is list:
                x = pos[0][0]
                y = pos[0][1]

                if (x < 5 and x > -5) and (y < 5 and y > -5):
                        self.curve.addPoints(x=[x],y=[y],pen='r', brush=pg.mkBrush(255, 0, 0, 255))
                else:
                        self.curve.addPoints(x=[x],y=[y],pen='g', brush=pg.mkBrush(0, 255, 0, 255))

        if type(wall) is list:
            for pos in wall:
                self.curve.addPoints(x=[pos[0]],y=[pos[1]],pen='r', brush=pg.mkBrush(255,0, 0, 255))

        self.prev = dataRow

if __name__ == '__main__':
    
    processedData = Queue()
    try:
        try:
            ip = sys.argv[1]	
        except:
            ip = "alphapi.local"
            #ip = "192.168.1.26"

        dataProcessingThread = Process(name = "Data Processing" ,target=data.processData, \
                kwargs ={'ip': ip, 'processedData': processedData})
        
        dataProcessingThread.daemon = True
        dataProcessingThread.start()

        scatter_plot(processedData)

    except Exception as e:
        print "Exception caught in graph module, "+ e
        sys.exit(0)

