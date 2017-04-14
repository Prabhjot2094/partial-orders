import smbus
import time

bus = smbus.SMBus(1)
address = 0x04
sensorCount = 11

sensorData = [0] * sensorCount

def highByte (number) : return number >> 8
def lowByte (number) : return number & 0x00FF
def getWord (lowByte, highByte) : return ((highByte << 8) | lowByte)

def writeMotorSpeeds(speedLeft, speedRight):
    try:
        bus.write_block_data(address, 0, [highByte(speedLeft), lowByte(speedLeft), highByte(speedRight), lowByte(speedRight)])
    except IOError:
        writeMotorSpeeds(speedLeft, speedRight)

def readSensorData():
    try:
        rawData = bus.read_i2c_block_data(address, 0)

        if (len(rawData) != 32):
            readSensorData()

        for sensorIndex in range(0, sensorCount):
            sensorData[sensorIndex] = getWord(rawData[2*sensorIndex + 1], rawData[2*sensorIndex + 0])
            if sensorData[sensorIndex] > 1023:
                readSensorData()

    except IOError:
        readSensorData()


while True:
    start = time.time()
    readSensorData()
    elapsed = time.time() - start
    print elapsed
    
    #var1 = input("Enter Left Speed: ")
    #var2 = input("Enter Right Speed: ")

    writeMotorSpeeds(0, 0)
    time.sleep(.250)
