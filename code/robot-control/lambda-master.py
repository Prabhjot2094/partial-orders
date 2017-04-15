import smbus
import time
import threading

# configuration variables
ARDUINO_ADDRESS             = 0x04  # i2c address for arduino
SENSOR_COUNT                = 11    # no of sensors on arduino
DATA_READ_INTERVAL          = 10    # milliseconds
AUTOPILOT_COMPUTE_INTERVAL  = 50    # milliseconds

bus = smbus.SMBus(1)

sensorData = [0] * (1 + SENSOR_COUNT)
sensorDataReady = False
dataReadFlag = False
averageInterval = 0

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

    dataReadFlag = True
    while True:
        pass
    

def writeMotorSpeeds(speedLeft, speedRight):
    try:
        bus.write_block_data(ARDUINO_ADDRESS, 0, [highByte(speedLeft), lowByte(speedLeft), highByte(speedRight), lowByte(speedRight)])
    except IOError:
        writeMotorSpeeds(speedLeft, speedRight)

def readSensorData():
    global sensorData
    global sensorDataReady
    global dataReadFlag

    nextDataReadTime = time.time()

    while True:
        if dataReadFlag:
            #sensorDataReady = False
            currentTime = time.time()
            if currentTime >= nextDataReadTime:
                nextDataReadTime += DATA_READ_INTERVAL/100.0
                print '{0:.8f}'.format(currentTime)        
                #time.sleep(0.001)
                

            #sensorDataReady = True
        
    '''
    try:
        sensorData[0] = time.time()
        rawData = bus.read_i2c_block_data(ARDUINO_ADDRESS, 0)

        if (len(rawData) != 32):
            readSensorData()


        for sensorIndex in range(1, SENSOR_COUNT + 1):
            sensorData[sensorIndex] = getWord(rawData[2*(sensorIndex-1) + 1], rawData[2*(sensorIndex-1) + 0])
            if sensorData[sensorIndex] > 1023:
                readSensorData()

    except IOError:
        readSensorData()
    '''

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

main()
