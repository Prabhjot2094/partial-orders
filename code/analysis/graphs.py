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

class line_graph_3d:
    def __init__(self,processedData):
    	self.processedData = processedData
        app = QtGui.QApplication([])

        self.p = gl.GLViewWidget()
        self.p.opts['distance'] = 400
        self.p.show()
        self.p.setWindowTitle('pyqtgraph example: GLLinePlotItem')

        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.p.addItem(gx)

        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.p.addItem(gy)
        
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)

        gx.scale(15,15, 0)
        gy.scale(15, 15, 0)
        gz.scale(15,15,0)
        
        self.p.addItem(gz)

        self.ptr = 0

        self.data = []

        self.plt = gl.GLLinePlotItem(color=pg.glColor((100,5*1.3)), width=1., antialias=True)
        self.p.addItem(self.plt)

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(0)
        QtGui.QApplication.instance().exec_()
        
    def update(self):
        if int(self.processedData.qsize()) is 0:
            return
        
        dataRow = self.processedData.get()
        self.data.append(dataRow)

        pts = np.vstack([[self.data]])

        self.plt.setData(pos = pts) 
        self.ptr += 1

class line_graph:
    def __init__(self,processedData):
    	self.processedData = processedData
        self.app = QtGui.QApplication([])

        self.p = pg.plot()
        self.p.setWindowTitle('pyqtgraph example: PlotSpeedTest')

        self.p.setLabel('bottom', 'Index')
        self.curve = self.p.plot()

        self.ptr = 0
        self.lastTime = time()
        self.fps = None

        self.datax = []
        self.datay = []

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(0)

        QtGui.QApplication.instance().exec_()

    def update(self):
        if int(self.processedData.qsize()) == 0:
            return
        
        dataRow = self.processedData.get()

        self.datax.append(dataRow[0])
        self.datay.append(dataRow[1])
        self.curve.setData(self.datax,self.datay,symbol='o')

        self.ptr += 1

        now = time()
        dt = now - self.lastTime
        self.lastTime = now
        
        if self.fps is None:
            self.fps = 1.0/dt
        else:
            s = np.clip(dt*3., 0, 1)
            self.fps = self.fps * (1-s) + (1.0/dt) * s
        
        self.p.setTitle('%0.2f fps' % self.fps)

class scatter_plot_3d:
    def __init__(self,processedData):
    	self.processedData = processedData
        app = QtGui.QApplication([])

        self.p = gl.GLViewWidget()
        self.p.opts['distance'] = 400
        self.p.show()
        self.p.setWindowTitle('pyqtgraph example: GLLinePlotItem')

        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.p.addItem(gx)

        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.p.addItem(gy)
        
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)

        gx.scale(15,15, 0)
        gy.scale(15, 15, 0)
        gz.scale(15,15,0)

        self.p.addItem(gz)

        self.ptr = 0

        self.data = [[0,0,0]]

        self.plt = gl.GLScatterPlotItem(color=pg.glColor((100,5*2.3)))
        self.p.addItem(self.plt)
        
        self.plt.color = pg.glColor((100,5*1.3))
        
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(0)
        QtGui.QApplication.instance().exec_()
        
    def update(self):
        if int(self.processedData.qsize()) is 0:
            return
        
        dataRow = self.processedData.get()

        self.data.append(dataRow)

        pts = np.vstack(self.data)

        self.plt.setData(pos = pts) 
        self.ptr += 1

class scatter_plot:
    def __init__(self,processedData):
        self.processedData = processedData
        app = QtGui.QApplication([])
        mw = QtGui.QMainWindow()

        self.p = pg.plot()

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
        x,y = float(dataRow[-2]), float(dataRow[-1])

        if self.prev == dataRow:
            self.prev = dataRow
            return
        print x,"  ",y
        self.curve.addPoints(x=[x],y=[y])
        self.prev = dataRow

if __name__ == '__main__':
    processedData = Queue()
    try:
        try:
            graphToPlot = sys.argv[1]	
            dataRequestParams = sys.argv[2:4]     
            autopilot = sys.argv[4]
        except:
            autopilot = 1
            graphToPlot = "scatter"
            dataRequestParams = ['c']

        if dataRequestParams[0]=='f':
            dataProcessingThread = Process(name = "Data Processing" ,target=data.processData, \
                    args = (dataRequestParams[0],dataRequestParams[1], processedData, autopilot,))
        
        elif dataRequestParams[0] in ['c','s']:
            dataProcessingThread = Process(name = "Data Processing" ,target=data.processData, \
                    args = (dataRequestParams[0],processedData,autopilot,))
        
        else:
          print "Incorrect Parameters for client, Requesting continuous data"
          dataProcessingThread = Process(name = "Data Processing" ,target=data.processData, \
                    args = (dataRequestParams[0],processedData,autopilot,))

        dataProcessingThread.daemon = True
        dataProcessingThread.start()

        if graphToPlot == "line":
            line_graph(processedData)
        
        elif graphToPlot == "line_3d":
            line_graph_3d(processedData)
        
        elif graphToPlot == "scatter":
            scatter_plot(processedData)
        
        elif graphToPlot == "scatter_3d":
            scatter_plot_3d(processedData)
        
        else:
            print "incorrect graph name, rendering scatter plot"
            scatter_plot(processedData)

    except Exception as e:
        print "Exception caught in graph module, "+str(e)
        sys.exit(0)
