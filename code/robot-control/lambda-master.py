import smbus
import time
import threading
import serial

# configuration variables
ARDUINO_ADDRESS             = 0x04  # i2c address for arduino
ARDUINO_DATA_COUNT          = 11    # no of sensors on arduino
SENSOR_TILE_DATA_COUNT      = 24
DATA_READ_INTERVAL          = 10    # milliseconds
AUTOPILOT_COMPUTE_INTERVAL  = 50    # milliseconds

arduinoBus = smbus.SMBus(1)
sensorTile = serial.Serial('/dev/ttyACM0', 9600)

sensorData = [0] * (1 + ARDUINO_DATA_COUNT + SENSOR_TILE_DATA_COUNT)
sensorDataReady = False
dataReadFlag = False

def highByte (number) : return number >> 8
def lowByte (number) : return number & 0x00FF
def getWord (lowByte, highByte) : return ((highByte << 8) | lowByte)


def main():
    global dataReadFlag

    try:
        dataReadThread = threading.Thread(target=readSensorData)
        dataReadThread.setDaemon(True)
        dataReadThread.start()
    except Exception as e:
        print "Exception in dataReadThread " + e
        shutdown()

    dataReadFlag = False

    while True:
        sensorTile.flushInput()
        print sensorTile.readline()
        time.sleep(0.500)


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
            rawData = sensorTile.readline()
            if len(rawData) == 24:
                for sensorIndex in range(0, SENSOR_TILE_DATA_COUNT):
                    sensorData[(1 + ARDUINO_DATA_COUNT) + sensorIndex] = rawData[sensorIndex]

            else:
                continue

    except Exception as e:
        print "Exception in sensorTileDataHandler " + e
        shutdown()


def writeMotorSpeeds(speedLeft, speedRight):
    try:
        arduinoBus.write_block_data(ARDUINO_ADDRESS, 0, [highByte(speedLeft), lowByte(speedLeft), highByte(speedRight), lowByte(speedRight)])
    except IOError:
        writeMotorSpeeds(speedLeft, speedRight)


def readSensorData():
    global sensorData
    global sensorDataReady
    global dataReadFlag

    nextDataReadTime = time.time()

    while True:
        if dataReadFlag:
            currentTime = time.time()
            if currentTime >= nextDataReadTime:
                sensorDataReady = False

                nextDataReadTime += DATA_READ_INTERVAL/100.0
                
                sensorData[0] = currentTime
                arduinoDataHandler()
                sensorTileDataHandler()

                sensorDataReady = True

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
