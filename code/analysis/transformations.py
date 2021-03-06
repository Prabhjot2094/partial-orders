import math
import sys
import csv
import time

def getFileName():
    return filePath.split('/')[-1].split('.')[0]

def getClass(value, classesList):
    for _class in classesList:
        lowerBound,upperBound = _class.split('-')[0],_class.split('-')[1]
        if int(value)>int(lowerBound) and int(value)<int(upperBound):
            return str(classesList.index(_class))
    return "-1"

def stepSize(columnName, classesList):
    with open(filePath, 'rb') as inputFile, open('transformations/stepSize/' + fileName + '_stepSize_' + columnName + '.csv', 'wb') as outputFile:
        spamInput = csv.reader(inputFile, delimiter=',')
        spamOutput = csv.writer(outputFile, delimiter=',')

        columnLabels = next(spamInput)

        try:
           columnIndex = columnLabels.index(columnName)
        except:
           print columnLabels
           return "Unknown column"

        firstRow = next(spamInput)

        previousValue = firstRow[columnIndex]
        previousClass = getClass(previousValue, classesList)

        print firstRow , columnIndex
        totalRows = transformedRows = 1
        for row in spamInput:
           totalRows+=1
           try:
               rowClass = getClass(row[columnIndex], classesList)
               if rowClass != previousClass:
                   transformedRows+=1
                   spamOutput.writerow([row[0],previousClass])
                   previousClass = rowClass
           except:
               continue


def definedMoves():
    columnName = "YAW"
    with open(filePath, 'rb') as inputFile, open('transformations/definedMoves/' + fileName + '_definedMoves_' + columnName + '.csv', 'wb') as outputFile:
        spamInput = csv.reader(inputFile, delimiter=',')
        spamOutput = csv.writer(outputFile, delimiter=',')

        columnLabels = next(spamInput)

        try:
           columnIndex = columnLabels.index(columnName)
        except:
           print columnLabels
           return "Unknown column"

        firstRow = next(spamInput)

        previousValue = int(float(firstRow[columnIndex]))
        previousState = 'Straight'
        
        delta = 1
        totalRows = transformedRows = 1
        for row in spamInput:
           totalRows+=1
           try:
               if int(float(row[columnIndex])) > (previousValue+delta):
                   if previousState != 'Left':
                       transformedRows+=1
                       spamOutput.writerow([row[0],previousState])
                   previousState = "Left"
               elif int(float(row[columnIndex])) < (previousValue-delta):
                   if previousState != 'Right':
                       transformedRows+=1
                       spamOutput.writerow([row[0],previousState])
                   previousState = "Right"
               elif int(float(row[columnIndex])) <=(previousValue+delta) and int(float(row[columnIndex]))>(previousValue-delta):
                   if previousState != 'Straight':
                       transformedRows+=1
                       spamOutput.writerow([row[0],previousState])
                   previousState = "Straight"
               previousValue = int(float(row[columnIndex]))
           except Exception as e:
           	   print e
           	   continue

        return "Transformation Successful"

def sameValues(columnName):
    with open(filePath, 'rb') as inputFile, open('transformations/sameValues/' + getFileName() + '_sameValues_' + columnName + '.csv', 'wb') as outputFile:
        spamInput = csv.reader(inputFile, delimiter=',')
        spamOutput = csv.writer(outputFile, delimiter=',')

        columnLabels = next(spamInput)

        try:
           columnIndex = columnLabels.index(columnName)
        except:
           return "Unknown column"

        previousValue = -1
        totalRows = transformedRows = 1
        for row in spamInput:
           totalRows+=1
           try:
               if int(row[columnIndex]) != int(previousValue):
                   transformedRows+=1
                   spamOutput.writerow([row[0], row[columnIndex]])
                   previousValue = row[columnIndex]
           except Exception as e:
           	   print e
           	   continue

        print totalRows,' ',transformedRows
        return "Transformation Successful"


def direction(columnName):
    with open(filePath, 'rb') as inputFile, open('transformations/direction/' + getFileName() + '_direction_' + columnName + '.csv', 'wb') as outputFile:
        spamInput = csv.reader(inputFile, delimiter=',')
        spamOutput = csv.writer(outputFile, delimiter=',')

        columnLabels = next(spamInput)

        try:
            columnIndex = columnLabels.index(columnName)
        except:
            return "Unknown column"

        totalRows = 0
        transformedRows = 0
        first = int(next(spamInput)[columnIndex])
        previous = int(next(spamInput)[columnIndex])

        direction = (0 if (first > previous) else 1)

        for row in spamInput:
            totalRows += 1
            if(int(row[columnIndex]) == 0):
                continue
            try:
                if previous < int(row[columnIndex]):
                    if direction == 1:
                        previous = int(row[columnIndex])
                        continue
                    else:
                        direction = 1
                        previous = int(row[columnIndex])
                        spamOutput.writerow([row[0], 0])
                        transformedRows += 1

                elif previous > int(row[columnIndex]):
                    if direction == 0:
                        previous = int(row[columnIndex])
                        continue
                    else:
                        direction = 0
                        previous = int(row[columnIndex])
                        spamOutput.writerow([row[0], 1])
                        transformedRows += 1

                else:
                    previous = int(row[columnIndex])
                    continue
            except Exception as e:
            	print e
                print row
                continue

        print "Total Rows: " + str(totalRows) + " Transformed Rows: " + str(transformedRows)
        return "Transformation Successful"


def rate(columnName, timeInterval):
    with open(filePath, 'rb') as inputFile, open('transformations/rate/' + getFileName() + '_rate_' + columnName + '.csv', 'wb') as outputFile:
        spamInput = csv.reader(inputFile, delimiter=',')
        spamOutput = csv.writer(outputFile, delimiter=',')

        columnLabels = next(spamInput)

        try:
            columnIndex = columnLabels.index(columnName)
        except:
            return "Unknown column"

        totalRows = 0
        transformedRows = 0
        first = next(spamInput)
        previous = next(spamInput)

        (direction, first)  = ((0, previous) if (int(first[columnIndex]) > int(previous[columnIndex])) 
                                else ((1, previous) if (int(first[columnIndex]) > int(previous[columnIndex])) else (1, first)))
        
        for row in spamInput:
            totalRows += 1
            if(int(row[columnIndex]) == 0):
                continue
            try:
                if int(previous[columnIndex]) < int(row[columnIndex]):
                    if direction == 1:
                        previous = row
                        continue
                    else:
                        direction = 1
                        previous = row
                        print (int(row[columnIndex]), int(first[columnIndex]))
                        rate_value = ((float(row[columnIndex]) - float(first[columnIndex])) / (float(row[0]) - float(first[0])))
                        spamOutput.writerow([row[0], rate_value])
                        transformedRows += 1

                elif int(previous[columnIndex]) > int(row[columnIndex]):
                    if direction == 0:
                        previous = row
                        continue
                    else:
                        direction = 0
                        previous = row
                        print (int(row[columnIndex]), int(first[columnIndex]))
                        rate_value = ((float(row[columnIndex]) - float(first[columnIndex])) / (float(row[0]) - float(first[0])))
                        spamOutput.writerow([row[0], rate_value])
                        transformedRows += 1

                else:
                    previous = row
                    continue
            except:
                print row
                continue

        print "Total Rows: " + str(totalRows) + " Transformed Rows: " + str(transformedRows)
        return "Transformation Successful"

def coordinates():
    with open(filePath, 'rb') as inputFile, open('../../data/transformations/sameValues/' + getFileName() + \
            '_sameValues_.csv', 'wb') as outputFile:
        
        spamInput = csv.reader(inputFile, delimiter=',')
        spamOutput = csv.writer(outputFile, delimiter=',')

        columnLabels = next(spamInput)

        try:
           yawColumn = columnLabels.index('YAW')
           usColumn = columnLabels.index('US_3')
        except:
           return "Unknown column"

        firstDataRow = next(spamInput)

        prevX = prevY = 0
        previousYaw = float(firstDataRow[yawColumn])
        previousDistance = float(firstDataRow[usColumn])
        
        for row in spamInput:
            currentYaw = float(row[yawColumn])
            currentDistance = float(row[usColumn])

            distanceDiff = previousDistance-currentDistance

            if currentYaw-previousYaw > 35:
                previousDistance = currentDistance
                prevousYaw = currentYaw
                continue

            x = math.cos(math.radians(currentYaw))*distanceDiff + prevX
            y = math.sin(math.radians(currentYaw))*distanceDiff + prevY

            spamOutput.writerow([row[0],row[yawColumn],row[usColumn],x,y])




#column = "US_3"
#ultrasonic_classes = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100', '101-110',
#                        '111-120', '121-130', '131-140', '141-150', '151-160', '161-170', '171-180', '181-190', '191-200']
filePath = sys.argv[1]
fileName = getFileName()
#print stepSize(column, ultrasonic_classes)
#print definedMoves()
#print sameValues(column)
#print direction(column)
#print rate(column, 10)

coordinates()

