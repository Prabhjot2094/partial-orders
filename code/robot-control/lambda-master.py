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
    bus.write_block_data(address, 0, [highByte(speedLeft), lowByte(speedLeft), highByte(speedRight), lowByte(speedRight)])

def readSensorData():
    rawData = bus.read_i2c_block_data(address, 0)
    for sensorIndex in range(0, sensorCount):
        sensorData[sensorIndex] = getWord(rawData[2*i + 1], rawData[2*i +0])

while True:
    readSensorData()

    print sensorData
    
    var1 = input("Enter Left Speed: ")
    var2 = input("Enter Right Speed: ")

    writeMotorSpeeds(var1, var2)