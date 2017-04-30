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

    def __init__(self,arduinoDataCount = 11, dataReadInterval = 50, obstacleDistance = 10, verboseDataReporting = False):
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

    def dataProcessor(self):
        self.processFromSonar()
    
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
        return time.time() - self.initialtime

    def arduinoDataHandler(self):
        try:
            rawData = self.arduinoBus.read_i2c_block_data(self.ARDUINO_ADDRESS, 0)

            if (len(rawData) != 32):
                self.readSensorData()

            for sensorIndex in range(1, self.ARDUINO_DATA_COUNT + 1):
                self.sensorData[sensorIndex] = self.getWord(rawData[2*(sensorIndex-1) + 1], rawData[2*(sensorIndex-1) + 0])
                if self.sensorData[sensorIndex] > 1023:
                    self.arduinoDataHandler()

        except IOError:
            self.arduinoDataHandler()

    def sensorTileDataHandler(self):
        try:
            self.sensorTile.flushInput()

            while True:
                rawData = self.sensorTile.readline().split(', ')
                if len(rawData) == 24:
                    for sensorIndex in range(0, self.SENSOR_TILE_DATA_COUNT):
                        if sensorIndex < 11:
                            self.sensorData[(1 + self.ARDUINO_DATA_COUNT) + sensorIndex] = int(rawData[sensorIndex])
                        else:
                            self.sensorData[(1 + self.ARDUINO_DATA_COUNT) + sensorIndex] = float(rawData[sensorIndex])
                    break

                else:
                    continue
        except:
            self.sensorTileDataHandler()

    def readSensorData(self):
        nextDataReadTime = self.getTimestamp()

        with open(self.getFileName(), 'wb') as rawfile:
            csvfile = csv.writer(rawfile, delimiter=',') 
            while True:
                if self.dataReadFlag:
                    currentTime = self.getTimestamp()
                    if currentTime >= nextDataReadTime:
                        self.sensorDataReady = False

                        nextDataReadTime += self.DATA_READ_INTERVAL/1000.0
                        
                        self.sensorData[0] = currentTime
                        self.arduinoDataHandler()
                        self.sensorTileDataHandler()
                       
                        if self.VERBOSE_DATA_REPORTING:
                            self.dataProcessor()
                            self.sensorDataQueue.put(self.sensorData)

                        self.sensorDataReady = True
                        if self.dataLogFlag:
                            csvfile.writerow(self.sensorData)
                        time.sleep(0.01)

                else:
                    time.sleep(0.01)

    def writeMotorSpeeds(self, speedLeft, speedRight):
        try:
            self.arduinoBus.write_block_data(self.ARDUINO_ADDRESS, 0, [self.highByte(int(speedLeft)), self.lowByte(int(speedLeft)), self.highByte(int(speedRight)), self.lowByte(int(speedRight))])
        except IOError:
            self.writeMotorSpeeds(speedLeft, speedRight)
        except Exception as e:
            print "Exception " + str(e)
            self.shutdown()

    def checkObstacle(self, sensorData, obstacleArray=[]):
        obstacleFlag = False
        obstacleSum = 0
        for sensorIndex in range(1, self.SONAR_NUM + 1):
            obstacleArray.append(self.sensorData[sensorIndex]) 
            if self.sensorData[sensorIndex] > 0 and self.sensorData[sensorIndex] < self.OBSTACLE_DISTANCE:
                obstacleSum += (sensorIndex - (self.SONAR_NUM +1)/2)
                obstacleFlag = True

        if obstacleFlag:
            return obstacleSum
        else:
            return 100

    def getSensorData(self):
        while not self.sensorDataReady:
            time.sleep(0.001)
            pass

        return self.sensorData

    def drive(self,command, speed=127, dataLog=True):
            self.dataReadFlag = True
            self.dataLogFlag = dataLog
            self.autopilotFlag = False

            if command == 'forward':
                    self.writeMotorSpeeds(speed, speed)

            if command == 'backward':
                    self.writeMotorSpeeds(-speed, -speed)

            if command == 'left':
                    self.writeMotorSpeeds(0, speed)

            if command == 'right':
                    self.writeMotorSpeeds(speed, 0)

            if command == 'stop':
                    self.writeMotorSpeeds(0, 0)

            if command == 'halt':
                    self.writeMotorSpeeds(0, 0)
                    self.dataReadFlag = False

            if command == 'autopilot-sonar':
                    try:
                            autopilotThread.join()
                    
                    except NameError:
                            self.autopilotFlag = True
                            
                            autopilotThread = threading.Thread(target=self.autopilot, args=('sonar', speed))
                            autopilotThread.setDaemon(True)
                            autopilotThread.start()
                    
                    self.autopilotStartTime = time.time()

            if command == 'autopilot-sonar-yaw':
                    try:
                            autopilotThread.join()
                    
                    except NameError:
                            self.autopilotFlag = True

                            autopilotThread = threading.Thread(target=self.autopilot, args=('sonar-yaw', speed))
                            autopilotThread.setDaemon(True)
                            autopilotThread.start()

    def shutdown(self):
        print "Shutting Down"
        self.writeMotorSpeeds(0, 0)
        sys.exit(0)
