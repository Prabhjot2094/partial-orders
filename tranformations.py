import csv
import time

def getClass(value, classesList):
    for _class in classesList:
        lowerBound,upperBound = _class.split('-')[0],_class.split('-')[1]
        if int(value)>int(lowerBound) and int(value)<int(upperBound):
            return _class
    return "No-Class"

def stepSize(columnName, classesList):
    with open('../record.csv', 'rb') as inputFile , open('../_'+columnName+'_definedMoves_record.csv', 'wb') as outputFile:
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
    with open('../record.csv', 'rb') as inputFile , open('../_'+columnName+'_definedMoves_record.csv', 'wb') as outputFile:
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
    with open('../record.csv', 'rb') as inputFile , open('../_'+columnName+'_sameValues_record.csv', 'wb') as outputFile:
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
    with open(filePath, 'rb') as inputFile, open(fileName + '_direction_' + columnName + '.csv', 'wb') as outputFile:
        spamInput = csv.reader(inputFile, delimiter=',')
        spamOutput = csv.writer(inputFile, delimiter=',')

        columnLabels = next(spamInput)

        try:
            columnIndex = columLabels.index(columnName)
        except:
            return "Unknown column"

        totalRows = 0
        first = int(next(spamInput)[columIndex])
        previous = int(next(spamInput)[columnIndex])

        direction = (0 if (first > previous) else 1)

        for row in spamInput:
            totalRows += 1
            try:
                if previous < int(row[columnIndex]):
                    if direction == 1:
                        previous = int(row[columIndex])
                        continue
                    else:
                        direction = 1
                        previous = int(row[columnIndex])
                        outFile.write("Decreasing")

                elif previous > int(row[columnIndex]):
                    if direction == 0:
                        previous = int(row[columnIndex])
                        continue
                    else:
                        direction = 0
                        previous = int(row[columnIndex])
                        outFile.write("Increasing")

                else:
                    previous = int(row[columnIndex])
                    continue
            except:
                print row
                continue

        print totalRows + "rows transformed."
        return "Transformation Successful"
