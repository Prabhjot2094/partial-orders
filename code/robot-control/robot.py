import math
from multiprocessing import Queue
import csv
import os
import smbus
import time
import threading
import serial
import sys

class Robot():

    # configuration variables
    ARDUINO_ADDRESS             = 0x04  # i2c address for arduino
    ARDUINO_DATA_COUNT          = 11    # no of sensors on arduino
    SENSOR_TILE_DATA_COUNT      = 24
    DATA_READ_INTERVAL          = 50    # milliseconds
    YAW_INDEX                   = 23
    US_INDEX                    = 3
    MAX_SPEED                   = 255
    TURN_ANGLE                  = 45
    OBSTACLE_DISTANCE           = 10
    MAX_DISTANCE_DIFF           = 25
    VERBOSE_DATA_REPORTING      = False
    DATA_SOURCE                 = 'sonar'       # sonar or encoders
    SONAR_NUM                   = 5
    ROBOT_SPEED                 = 10

    arduinoBus = smbus.SMBus(1)
    try:
        sensorTile = serial.Serial('/dev/ttyACM0', 9600)
    except:
        sensorTile = serial.Serial('/dev/ttyACM1', 9600)

    sensorData = [0] * (1 + ARDUINO_DATA_COUNT + SENSOR_TILE_DATA_COUNT + 2)
    sensorDataReady = False
    dataReadFlag = False
    dataLogFlag = False
    autopilotFlag = False
    initialtime = 0
    autopilotStartTime = 0
    sensorDataQueue = Queue()

    def __init__(arduinoDataCount = 11, dataReadInterval = 50, obstacleDistance = 10, verboseDataReporting = False):
        self.ARDUINO_DATA_COUNT = arduinoDataCount
        self.DATA_READ_INTERVAL = dataReadInterval
        self.OBSTACLE_DISTANCE = obstacleDistance
        self.VERBOSE_DATA_REPORTING = verboseDataReporting
        
    def highByte (self, number) : return number >> 8
    def lowByte (self, number) : return number & 0x00FF
    def getWord (self, lowByte, highByte): 
        word = ((highByte << 8) | lowByte)
        if word > 32767:
            word -= 65536

        return word

    def getFileName(self):
        directory = '../../data/live-data'
        if not os.path.exists(directory):
            os.makedirs(directory)
        number = 0
        while True:
            fileNamePath = directory + ('/record_%d.csv' % number)
            if not os.path.exists(fileNamePath):
                return fileNamePath
            else:
                number += 1

    def getTimestamp(self):
        return time.time() - initialtime

    def arduinoDataHandler(self):
        sensorData = self.sensorData

        try:
            rawData = arduinoBus.read_i2c_block_data(ARDUINO_ADDRESS, 0)

            if (len(rawData) != 32):
                readSensorData()

            for sensorIndex in range(1, ARDUINO_DATA_COUNT + 1):
                sensorData[sensorIndex] = getWord(rawData[2*(sensorIndex-1) + 1], rawData[2*(sensorIndex-1) + 0])
                if sensorData[sensorIndex] > 1023:
                    arduinoDataHandler()

        except IOError:
            arduinoDataHandler()

    def sensorTileDataHandler(self):
        sensorData = self.sensorData

        try:
            sensorTile.flushInput()

            while True:
                rawData = sensorTile.readline().split(', ')
                if len(rawData) == 24:
                    for sensorIndex in range(0, SENSOR_TILE_DATA_COUNT):
                        if sensorIndex < 11:
                            sensorData[(1 + ARDUINO_DATA_COUNT) + sensorIndex] = int(rawData[sensorIndex])
                        else:
                            sensorData[(1 + ARDUINO_DATA_COUNT) + sensorIndex] = float(rawData[sensorIndex])
                    break

                else:
                    continue
        except:
            sensorTileDataHandler()

    def readSensorData(self):
        sensorData = self.sensorData
        sensorDataReady = self.sensorDataReady
        dataReadFlag = self.dataReadFlag
        dataLogFlag = self.dataLogFlag

        nextDataReadTime = getTimestamp()

        with open(getFileName(), 'wb') as rawfile:
            csvfile = csv.writer(rawfile, delimiter=',') 
            while True:
                if dataReadFlag:
                    currentTime = getTimestamp()
                    if currentTime >= nextDataReadTime:
                        sensorDataReady = False

                        nextDataReadTime += DATA_READ_INTERVAL/1000.0
                        
                        sensorData[0] = currentTime
                        arduinoDataHandler()
                        sensorTileDataHandler()
                        
                        if VERBOSE_DATA_REPORTING:
                            dataProcessor()
                            sensorDataQueue.put(sensorData)

                        sensorDataReady = True

                        if dataLogFlag:
                            csvfile.writerow(sensorData)
                        time.sleep(0.01)

                else:
                    time.sleep(0.01)

    def writeMotorSpeeds(self, speedLeft, speedRight):
        try:
            arduinoBus.write_block_data(ARDUINO_ADDRESS, 0, [highByte(int(speedLeft)), lowByte(int(speedLeft)), highByte(int(speedRight)), lowByte(int(speedRight))])
        except IOError:
            writeMotorSpeeds(speedLeft, speedRight)
        except Exception as e:
            print "Exception " + str(e)
            shutdown()

    def checkObstacle(self, sensorData, obstacleArray=[]):
        obstacleFlag = False
        obstacleSum = 0
        for sensorIndex in range(1, SONAR_NUM + 1):
            obstacleArray.append(sensorData[sensorIndex]) 
            if sensorData[sensorIndex] > 0 and sensorData[sensorIndex] < OBSTACLE_DISTANCE:
                obstacleSum += (sensorIndex - (SONAR_NUM +1)/2)
                obstacleFlag = True

        if obstacleFlag:
            return obstacleSum
        else:
            return 100

    def getSensorData(self):
        sensorDataReady = self.sensorDataReady
        sensorData = self.sensorData

        while not sensorDataReady:
            pass

        return sensorData

	def drive(self,command, speed=127, dataLog=True):
		dataReadFlag = self.dataReadFlag
		dataLogFlag = self.dataLogFlag
		autopilotFlag = self.autopilotFlag
		autopilotStartTime = self.autopilotStartTime
		
		dataReadFlag = True
		dataLogFlag = dataLog
		autopilotFlag = False

		if command == 'forward':
			writeMotorSpeeds(speed, speed)

		if command == 'backward':
			writeMotorSpeeds(-speed, -speed)

		if command == 'left':
			writeMotorSpeeds(0, speed)

		if command == 'right':
			writeMotorSpeeds(speed, 0)

		if command == 'stop':
			writeMotorSpeeds(0, 0)

		if command == 'halt':
			writeMotorSpeeds(0, 0)
			dataReadFlag = False

		if command == 'autopilot-sonar':
			try:
				autopilotThread.join()
			
			except NameError:
				autopilotFlag = True

				autopilotThread = threading.Thread(target=autopilot, args=('sonar', speed))
				autopilotThread.setDaemon(True)
				autopilotThread.start()
			
			autopilotStartTime = time.time()

		if command == 'autopilot-sonar-yaw':
			try:
				autopilotThread.join()
			
			except NameError:
				autopilotFlag = True

				autopilotThread = threading.Thread(target=autopilot, args=('sonar-yaw', speed))
				autopilotThread.setDaemon(True)
				autopilotThread.start()

    def shutdown(self):
        print "Shutting Down"
        writeMotorSpeeds(0, 0)
        sys.exit(0)
