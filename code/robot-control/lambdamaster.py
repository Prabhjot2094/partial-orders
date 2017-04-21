from multiprocessing import Queue
import csv
import os
import smbus
import time
import threading
import serial
import sys
import PID

# configuration variables
ARDUINO_ADDRESS             = 0x04  # i2c address for arduino
ARDUINO_DATA_COUNT          = 11    # no of sensors on arduino
SENSOR_TILE_DATA_COUNT      = 24
DATA_READ_INTERVAL          = 50    # milliseconds
AUTOPILOT_UPDATE_INTERVAL   = 50    # milliseconds
YAW_P                       = 1.5
YAW_I                       = 0.0
YAW_D                       = 0.0
YAW_INDEX                   = 23
MAX_SPEED                   = 255
TURN_ANGLE                  = 45
OBSTACLE_DISTANCE           = 18

arduinoBus = smbus.SMBus(1)
try:
    sensorTile = serial.Serial('/dev/ttyACM0', 9600)
except:
    sensorTile = serial.Serial('/dev/ttyACM1', 9600)

sensorData = [0] * (1 + ARDUINO_DATA_COUNT + SENSOR_TILE_DATA_COUNT)
sensorDataReady = False
dataReadFlag = False
dataLogFlag = False
autopilotFlag = False
initialtime = 0
sensorDataQueue = Queue()

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

        dataReadFlag = False

        #drive('autopilot-sonar', 255, False)
        #while True:
        #    time.sleep(0.01)

    except KeyboardInterrupt:
        shutdown()

    except Exception as e:
        print "Exception in main " + str(e)
        shutdown()
        raise

def getFileName():
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

    except:
        sensorTileDataHandler()

def writeMotorSpeeds(speedLeft, speedRight):
    try:
        arduinoBus.write_block_data(ARDUINO_ADDRESS, 0, [highByte(int(speedLeft)), lowByte(int(speedLeft)), highByte(int(speedRight)), lowByte(int(speedRight))])
    except IOError:
        writeMotorSpeeds(speedLeft, speedRight)
    except Exception as e:
        print "Exception " + str(e)
        shutdown()

def readSensorData():
    global sensorDataQueue
    global sensorData
    global sensorDataReady
    global dataReadFlag
    global dataLogFlag

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
                    sensorDataQueue.put(sensorData)
                    if dataLogFlag:
                        csvfile.writerow(sensorData)

            else:
                time.sleep(0.01)

def checkObstacle(sensorData, obstacleArray=[]):
    obstacleFlag = False
    obstacleSum = 0
    for sensorIndex in range(1, 6):
        obstacleArray.append(sensorData[sensorIndex]) 
        if sensorData[sensorIndex] > 0 and sensorData[sensorIndex] < OBSTACLE_DISTANCE:
            obstacleSum += (sensorIndex - 3)
            obstacleFlag = True

    if obstacleFlag:
        return obstacleSum
    else:
        return 100

def getSensorData():
    global sensorDataReady
    global sensorData

    while not sensorDataReady:
        pass

    return sensorData

def drive(command, speed=127, dataLog=True):
    global dataReadFlag
    global dataLogFlag
    global autopilotFlag
    
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

    if command == 'autopilot-sonar-yaw':
        try:
            autopilotThread.join()
        
        except NameError:
            autopilotFlag = True

            autopilotThread = threading.Thread(target=autopilot, args=('sonar-yaw', speed))
            autopilotThread.setDaemon(True)
            autopilotThread.start()

def autopilot(type='sonar', speed=255):
    global autopilotFlag

    nextAutopilotUpdateTime = getTimestamp()

    if type == 'sonar-yaw':
        robotPID = PID.PID(YAW_P, YAW_I, YAW_D)
        robotPID.setPoint = getSensorData()[YAW_INDEX]
        robotPID.setSampleTime(AUTOPILOT_UPDATE_INTERVAL/1000.0)

    while True:
        if autopilotFlag:
            currentTime = getTimestamp()
            if currentTime >= nextAutopilotUpdateTime:
                nextAutopilotUpdateTime += AUTOPILOT_UPDATE_INTERVAL/1000.0

                sensorData = getSensorData()

                if type == 'sonar':
                    obstacle = checkObstacle(sensorData)

                    if obstacle == 100:     # no obstacle
                        writeMotorSpeeds(speed, speed)
                    elif obstacle < 0:      # obstacle towards left
                        writeMotorSpeeds(speed, -speed)
                        time.sleep(.500)
                        writeMotorSpeeds(0, 0)
                    elif obstacle >= 0:     # obstacle towards right or in front
                        writeMotorSpeeds(-speed, speed)
                        time.sleep(.500)
                        writeMotorSpeeds(0, 0)

                elif type == 'sonar-yaw':
                    obstacleArray = []
                    obstacle = checkObstacle(sensorData, obstacleArray)

                    if obstacleArray[2] == 0:
                        writeMotorSpeeds(0, 0)

                    elif obstacle == 100:
                        feedback = sensorData[YAW_INDEX] - robotPID.setPoint

                        if feedback < -180.0:
                            feedback += 360
                        elif feedback > 180:
                            feedback -= 360

                        robotPID.update(feedback)
                        pidOutput = int(robotPID.output)

                        if pidOutput < 0:
                            writeMotorSpeeds(MAX_SPEED + pidOutput, MAX_SPEED)      # turn left if PID output is -ve
                        else:
                            writeMotorSpeeds(MAX_SPEED, MAX_SPEED - pidOutput)      # turn right if PID output is +ve

                    elif obstacle < 0:
                        robotPID.setPoint += TURN_ANGLE
                        if robotPID.setPoint > 180:
                            robotPID.setPoint -= 360

                        writeMotorSpeeds(speed*0.5, -speed*0.5)
                        while (robotPID.setPoint - getSensorData()[YAW_INDEX])  > 10:
                            pass
                        else:
                            writeMotorSpeeds(0, 0)

                    else:
                        robotPID.setPoint -= TURN_ANGLE
                        if robotPID.setPoint < -180:
                            robotPID.setPoint += 360

                        writeMotorSpeeds(-speed*0.5, speed*0.5)
                        while getSensorData()[YAW_INDEX] - robotPID.setPoint > 10:
                            pass
                        else:
                            writeMotorSpeeds(0, 0)

        else:
            return

def shutdown():
    print "Shutting Down"
    writeMotorSpeeds(0, 0)
    sys.exit(0)

main()
