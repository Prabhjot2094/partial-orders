import smbus
import time

bus = smbus.SMBus(1)

address = 0x04

def writeNumber(cmd, value):
    bus.write_block_data(address, cmd, value)
    # bus.write_byte_data(address, 0, value)
    return -1

def readNumber():
    number = bus.read_byte(address)
    # number = bus.read_byte_data(address, 1)
    return number

while True:
    var1 = input("Enter Left Speed: ")
    var2 = input("Enter Right Speed: ")

    writeNumber(0, [var1, var2])
    #writeNumber(1, var2)
    # sleep one second
