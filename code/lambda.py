from readchar import readchar
import smbus
import sys
from threading import Thread
import Queue
import csv
import ntplib
import time
import os.path
import serial

ser = serial.Serial('/dev/ttyACM0', 9600)

bus = smbus.SMBus(1)
direction = {'q':10, 'w':1, 'a':2, 'd':3, 's':4, 'p':5}

def next_file_name():
    num = 1
    while True:
        file_name = 'record%d.csv' % num
        if not os.path.exists(file_name):
            return file_name
        num += 1

def map(unmappedData):
    mappedData = []
    checksum = (unmappedData[0] << 8) | unmappedData[1]
    if sum(unmappedData[2:24]) == checksum:
        for i in range(2,24,2):
            temp = unmappedData[i] << 8
            mappedData.append(temp | unmappedData[i+1])
    return mappedData


def runRobot():
    count = 0
    print "Welcome to Westworld"
    while 1:
        userInput = readchar()
        print userInput
        if userInput == 'x':
            bus.write_byte(0x04,10)
            print "Exiting from Thread"
            return
        elif userInput == 'p':
            if count%2 == 0:
                print "JARVIS: Autopilot Mode on."
            else:
                print "JARVIS: Autopilot Mode off."
            count = count + 1

        try:
            input = direction[userInput]
            bus.write_byte(0x04,input)
        except:
            continue


#Start Thread for user interaction on terminal
thread = Thread(target=runRobot, args = ())
thread.start()

#create csv file
#csvObj = createFile()
fileName = next_file_name()
csvFile = open(fileName,'wb', 0)
csvObj = csv.writer(csvFile,delimiter=',')

header = ['Timestamp', 'Calbration Flag', \
        'ACC_X', 'ACC_Y', 'ACC_Z', \
        'MAG_X', 'MAG_Y', 'MAG_Z', \
        'GYR_X', 'GYR_Y', 'GYR_Z', \
        'YAW', 'PITCH', 'ROLL', \
        'QUAT_0', 'QUAT_1', 'QUAT_2', 'QUAT_3', \
        'GRA_X', 'GRA_Y', 'GRA_Z', \
        'LIN_X', 'LIN_Y', 'LIN_Z', \
        'LDR1','LDR2','LDR3','LDR4','LDR5','LDR6', \
        'US_1', 'US_2', 'US_3', 'US_4', 'US_5']
csvObj.writerow(header)
print "CSV Created"
#return csvObj


#writing data to file

while 1:
    try:
        data = ser.readline().split(", ")
        if len(data) == 24:
            data[23] = float(data[23])
            i2c_unmapped = bus.read_i2c_block_data(0x04,0)
            mappedData = map(i2c_unmapped)
            if mappedData != []:
                finalData = data + mappedData
                csvObj.writerow(finalData)

    except(KeyboardInterrupt):
        #csvFile.close()
        sys.exit()
    except:
        continue

