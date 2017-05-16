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
    YAW_INDEX                   = 11
    US_INDEX                    = 3
    MAX_SPEED                   = 255
    TURN_ANGLE                  = 45
    OBSTACLE_DISTANCE           = 25
    MAX_DISTANCE_DIFF           = 25
    VERBOSE_DATA_REPORTING      = False
    DATA_SOURCE                 = 'sonar'       # sonar or encoders
    SONAR_NUM                   = 5
    LDR_NUM                     = 0
    ENCODER_NUM                 = 2
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
    leftLastTicks = rightLastTicks = 0

    def __init__(self,arduinoDataCount = 11, sonar_num = 3, ldr_num = 0, encoder_num = 2, dataReadInterval = 50, obstacleDistance = 10, verboseDataReporting = False):
        self.ARDUINO_DATA_COUNT = arduinoDataCount
        self.DATA_READ_INTERVAL = dataReadInterval
        self.OBSTACLE_DISTANCE = obstacleDistance
        self.VERBOSE_DATA_REPORTING = verboseDataReporting
        self.SONAR_NUM = sonar_num
        self.LDR_NUM = ldr_num
        self.ENCODER_NUM = encoder_num
        self.YAW_INDEX = 1 + self.ARDUINO_DATA_COUNT + 11
        
    def highByte (self, number) : return number >> 8
    def lowByte (self, number) : return number & 0x00FF
    def getWord (self, lowByte, highByte): 
        word = ((highByte << 8) | lowByte)
        if word > 32767:
            word -= 65536
        return word

    def checkCRC (self, data, crcIndex):
        CRC7_POLY = 0x91
        crc = 0

        for i in range(0, crcIndex):
            crc ^= data[i]

            for j in range(0, 8):
                if (crc & 1):
                    crc ^= CRC7_POLY
                crc >>= 1

        if crc == data[crcIndex]:
            return True
        else:
            return False

    def getDoubleWord(self, bytesList):
        doubleWord = 0
        for byte in bytesList:
            doubleWord = ((doubleWord << 8) | byte)

        if doubleWord > 2147483647:
            doubleWord -= 4294967296

        return doubleWord
    
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
                return False

            if not self.checkCRC(rawData, 14):
                return False

            for sensorIndex in range(1, self.SONAR_NUM + self.LDR_NUM + 1):
                self.sensorData[sensorIndex] = self.getWord(rawData[2*(sensorIndex-1) + 1], rawData[2*(sensorIndex-1) + 0])
                if self.sensorData[sensorIndex] > 200:
                    return False

            self.sensorData[4] = self.getDoubleWord([rawData[6], rawData[7], rawData[8], rawData[9]])
            self.sensorData[5] = self.getDoubleWord([rawData[10], rawData[11], rawData[12], rawData[13]])

            if (abs(self.sensorData[4] - self.leftLastTicks) > 1000) or (abs(self.sensorData[5] - self.rightLastTicks) > 1000):
                return False
            else:
                self.leftLastTicks = self.sensorData[4]
                self.rightLastTicks = self.sensorData[5]

        except IOError:
            return False

        return True

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
            return False

        return True

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
                        while not self.arduinoDataHandler():
                            pass
                        while not self.sensorTileDataHandler():
                            pass

                        if self.VERBOSE_DATA_REPORTING:
                            if self.dataProcessor():
                                print "True"
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
                    self.writeMotorSpeeds(speed-3, speed-5)

            if command == 'backward':
                    self.writeMotorSpeeds(-speed, -speed)

            if command == 'left':
                    self.writeMotorSpeeds(0, speed)

            if command == 'right':
                    self.writeMotorSpeeds(speed, 0)

            if command == 'circle':
                    self.writeMotorSpeeds(speed, speed/2);

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

    def shutdown(self):
        print "Shutting Down"
        self.writeMotorSpeeds(0, 0)
        sys.exit(0)
