import smbus
import time

bus = smbus.SMBus(1)

address = 0x04

def highByte (number) : return number >> 8
def lowByte (number) : return number & 0x00FF

def sendMotorSpeeds(speedLeft, speedRight):
    bus.write_block_data(address, 0, [lowByte(speedLeft), highByte(speedLeft), lowByte(speedRight), highByte(speedRight)])

def readNumber():
    number = bus.read_byte(address)

    return number

while True:
    var1 = input("Enter Left Speed: ")
    var2 = input("Enter Right Speed: ")

    sendMotorSpeeds(var1, var2)