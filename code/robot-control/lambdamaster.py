import csv
import os
import smbus
import time
import threading
import serial
import sys

# configuration variables
ARDUINO_ADDRESS             = 0x04  # i2c address for arduino
ARDUINO_DATA_COUNT          = 11    # no of sensors on arduino
SENSOR_TILE_DATA_COUNT      = 24
DATA_READ_INTERVAL          = 100    # milliseconds
AUTOPILOT_COMPUTE_INTERVAL  = 50    # milliseconds

arduinoBus = smbus.SMBus(1)
try:
    sensorTile = serial.Serial('/dev/ttyACM0', 9600)
except:
    sensorTile = serial.Serial('/dev/ttyACM1', 9600)

sensorData = [0] * (1 + ARDUINO_DATA_COUNT + SENSOR_TILE_DATA_COUNT)
sensorDataReady = False
dataReadFlag = False
initialtime = 0

def highByte (number) : return number >> 8
def lowByte (number) : return number & 0x00FF
def getWord (lowByte, highByte) : return ((highByte << 8) | lowByte)

def main():
    try:
        global dataReadFlag
        global sensorDataReady
        global sensorData
        global initialtime

        initialtime = time.time()

        try:
            dataReadThread = threading.Thread(target=readSensorData)
            dataReadThread.setDaemon(True)
            dataReadThread.start()
        except Exception as e:
            print "Exception in dataReadThread " + str(e)
            shutdown()

        dataReadFlag = True

        while True:
            drive('forward', 255)
            time.sleep(1)
            drive('stop')
            time.sleep(1)

    except KeyboardInterrupt:
        shutdown()

def getFileName():
    number = 0
    while True:
        fileNamePath = '../../data/live-data/record_%d.csv' % number
        if not os.path.exists(fileNamePath):
            return fileNamePath
        else:
            number += 1

def getTimestamp():
    return time.time() - initialtime

def arduinoDataHandler():
    global sensorData

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

def sensorTileDataHandler():
    global sensorData

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

    except Exception as e:
        print "Exception in sensorTileDataHandler " + str(e)
        shutdown()

def writeMotorSpeeds(speedLeft, speedRight):
    try:
        while not sensorDataReady:
            pass
        arduinoBus.write_block_data(ARDUINO_ADDRESS, 0, [highByte(speedLeft), lowByte(speedLeft), highByte(speedRight), lowByte(speedRight)])
    except IOError:
        writeMotorSpeeds(speedLeft, speedRight)

def readSensorData():
    global sensorData
    global sensorDataReady
    global dataReadFlag

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

                    sensorDataReady = True
                    csvfile.writerow(sensorData)

            else:
                time.sleep(0.01)

def drive(command, speed=127):
    global dataReadFlag
    
    dataReadFlag = True

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
        pass

    if command == 'autopilot-sonar-yaw':
        pass

def shutdown():
    writeMotorSpeeds(0, 0)
    sys.exit(0)

main()
