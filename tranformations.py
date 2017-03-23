import sys
import csv
import time

def getFileName():
    return filePath.split('/')[-1].split('.')[0]

def getClass(value, classesList):
    for _class in classesList:
        lowerBound,upperBound = _class.split('-')[0],_class.split('-')[1]
        if int(value)>int(lowerBound) and int(value)<int(upperBound):
            return _class
    return "No-Class"

def stepSize(columnName, classesList):
    with open(filePath, 'rb') as inputFile, open('records/' + fileName + '_direction_' + columnName + '.csv', 'wb') as outputFile:
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
                   spamOutput.writerow([previousClass])
                   previousClass = rowClass
           except:
               continue


def definedMoves():
    columnName = "YAW"
    with open(filePath, 'rb') as inputFile, open('records/' + fileName + '_direction_' + columnName + '.csv', 'wb') as outputFile:
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
        previousState = 'Straight'

        totalRows = transformedRows = 1
        for row in spamInput:
           totalRows+=1
           try:
               if row[columnIndex] > previousValue:
                   if previousState != 'Left':
                       transformedRows+=1
                       spamOutput.writerow([previousState])
                   previousState = "Left"
               elif row[columnIndex] < previousValue:
                   if previousState != 'Right':
                       transformedRows+=1
                       spamOutput.writerow([previousState])
                   previousState = "Right"
               elif row[columnIndex] == previousValue:
                   if previousState != 'Straight':
                       transformedRows+=1
                       spamOutput.writerow([previousState])
                   previousState = "Straight"
               previousValue = row[columnIndex]
           except:
               continue

        return "Transformation Successful"

def sameValues(columnName):
    with open(filePath, 'rb') as inputFile, open('records/' + getFileName() + '_direction_' + columnName + '.csv', 'wb') as outputFile:
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
                   spamOutput.writerow([row[columnIndex]])
                   previousValue = row[columnIndex]
           except:
               print row
               continue

        print totalRows,' ',transformedRows
        return "Transformation Successful"


def direction(columnName):
    with open(filePath, 'rb') as inputFile, open('records/' + getFileName() + '_direction_' + columnName + '.csv', 'wb') as outputFile:
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
                        previous = int(row[columIndex])
                        continue
                    else:
                        direction = 1
                        previous = int(row[columnIndex])
                        spamOutput.writerow([row[0], "Decreasing"])
                        transformedRows += 1

                elif previous > int(row[columnIndex]):
                    if direction == 0:
                        previous = int(row[columnIndex])
                        continue
                    else:
                        direction = 0
                        previous = int(row[columnIndex])
                        spamOutput.writerow([row[0], "Increasing"])
                        transformedRows += 1

                else:
                    previous = int(row[columnIndex])
                    continue
            except:
                print row
                continue

        print "Total Rows: " + str(totalRows) + " Transformed Rows: " + str(transformedRows)
        return "Transformation Successful"


def rate(columnName, timeInterval):
    with open(filePath, 'rb') as inputFile, open('records/' + getFileName() + '_rate_' + columnName + '.csv', 'wb') as outputFile:
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


filePath = sys.argv[1]
#print direction("US_3")
print rate("US_3", 10)
