import smbus
import time

bus = smbus.SMBus(1)

address = 0x04

def highByte (number) : return number >> 8
def lowByte (number) : return number & 0x00FF
def getWord (lowByte, highByte) : return ((highByte << 8) | lowByte)

def sendMotorSpeeds(speedLeft, speedRight):
    bus.write_block_data(address, 0, [highByte(speedLeft), lowByte(speedLeft), highByte(speedRight), lowByte(speedRight)])

def readNumber():
    data = bus.read_i2c_block_data(address, 0)
    print number

while True:
    var1 = input("Enter Left Speed: ")
    var2 = input("Enter Right Speed: ")

    sendMotorSpeeds(var1, var2)

    readNumber()