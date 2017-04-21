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
        self.lastTime = time()
        self.fps = None

        self.dx=[random.randint(1,100) for i in range(1000)]
        self.dy=[random.randint(1,100) for i in range(1000)]

        self.datax = []
        self.datay = []


        self.plt = gl.GLLinePlotItem(color=pg.glColor((100,5*1.3)), width=1., antialias=True)
        self.p.addItem(self.plt)
        self.prev = [0,0,0]

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(0)
        QtGui.QApplication.instance().exec_()
        
    def update(self):
		if int(self.processedData.qsize()) is 0:
			return
		dataRow = self.processedData.get()

		self.datax.append(dataRow)

		x = dataRow[0]
		y = dataRow[1]
		z = dataRow[2]

		pts = np.vstack([[self.datax]])

		self.prev = [x,y,z]
		#pts = np.vstack([[1,1,1],[2,2,2],[3,3,3]])

		self.plt.setData(pos = pts) 
		self.ptr += 1

		now = time()
		dt = now - self.lastTime
		self.lastTime = now
		if self.fps is None:
				self.fps = 1.0/dt
		else:
				s = np.clip(dt*3., 0, 1)
				self.fps = self.fps * (1-s) + (1.0/dt) * s
		#self.p.setTitle('%0.2f fps' % fps)
		#p.show()
		#app.processEvents()  ## force complete redraw for every plot

class line_graph:
    def __init__(self,processedData):
    	self.processedData = processedData
        self.app = QtGui.QApplication([])

        self.p = pg.plot()
        self.p.setWindowTitle('pyqtgraph example: PlotSpeedTest')

        #QRectF(X_lb,Y_lb,X_ub,Y_ub)
        #p.setRange(QtCore.QRectF(0, 0, 1000, 1000)) 

        self.p.setLabel('bottom', 'Index')
        self.curve = self.p.plot()

        self.ptr = 0
        self.lastTime = time()
        self.fps = None

        self.dx=[random.randint(1,2000) for i in range(1000)]
        self.dy=[random.randint(1,1000) for i in range(1000)]

        self.datax = []
        self.datay = []

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(0)

        QtGui.QApplication.instance().exec_()

    def update(self):
        #global curve, data, ptr, p, lastTime, fps
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
        #app.processEvents()  ## force complete redraw for every plot

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

        data = np.random.normal(size=(50,5000))
        self.ptr = 0
        self.lastTime = time()
        self.fps = None

        self.dx=[random.randint(1,100) for i in range(1000)]
        self.dy=[random.randint(1,100) for i in range(1000)]

        self.datax = [[0,0,0]]
        self.datay = []


        self.plt = gl.GLScatterPlotItem(color=pg.glColor((100,5*2.3)))
        self.p.addItem(self.plt)
        self.prev = [0,0,0]
        
        self.plt.color = pg.glColor((100,5*1.3))
        
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(0)
        QtGui.QApplication.instance().exec_()
        
    def update(self):
		if int(self.processedData.qsize()) is 0:
				return
		dataRow = self.processedData.get()

		self.datax.append(dataRow)

		x = self.dx[self.ptr%1000]
		y = self.dx[self.ptr%1000]

		pts = np.vstack(self.datax)

		self.prev = [x,y,x]
		#pts = np.vstack([[1,1,1],[2,2,2],[3,3,3]])

		self.plt.setData(pos = pts) 
		self.ptr += 1

		now = time()
		dt = now - self.lastTime
		self.lastTime = now
		if self.fps is None:
				self.fps = 1.0/dt
		else:
				s = np.clip(dt*3., 0, 1)
				self.fps = self.fps * (1-s) + (1.0/dt) * s
		#self.p.setTitle('%0.2f fps' % fps)
		#p.show()
		#app.processEvents()  ## force complete redraw for every plot


class scatter_plot:
	def __init__(self,processedData):
		self.processedData = processedData
		app = QtGui.QApplication([])
		mw = QtGui.QMainWindow()

		self.p = pg.plot()
		#p.setRange(xRange=[-500, 500], yRange=[-500, 500])

		self.ptr = 0

		self.dx = [random.randint(1,1000) for i in range(1,1000)]
		self.dy = [random.randint(1,1000) for i in range(1,1000)]

		self.datax = []
		self.datay = []
		
		self.curve = pg.ScatterPlotItem(x=self.datax, y=self.datay,pen='r',symbol='o')
		self.p.addItem(self.curve)
		
		timer = QtCore.QTimer()
		timer.timeout.connect(self.update)
		timer.start(0)

		QtGui.QApplication.instance().exec_()
	
	def update(self):
		#global curve, data, ptr, p, lastTime, fps
		#p.clear()
		if int(self.processedData.qsize()) is 0:
				return
		dataRow = self.processedData.get()

		self.curve.addPoints([dataRow[0]],[dataRow[1]])

		#self.p.repaint()
		#app.processEvents()  ## force complete redraw for every plot


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    processedData = Queue()
    try:
        try:
			graphToPlot = sys.argv[1]		#line, scatter,scatter_3d,line_3d aas first parameter
			dataRequestParams = sys.argv[2:4]        #(c), (s), (f,frequency)
			autopilot = sys.argv[4]
        except:
			#Default graph and Request parameters
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
