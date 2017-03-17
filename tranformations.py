import csv
import time

temp = []

def definedMoves():
    columnName = "YAW"
    with open('../../Downloads/record(1).csv', 'rb') as inputFile , open('../../Downloads/_'+columnName+'_definedMoves_record.csv', 'wb') as outputFile:
       spamreader = csv.reader(inputFile, delimiter=',')
       columnLabels = next(spamreader)

       try:
           columnIndex = columnLabels.index(columnName)
       except:
           print columnLabels
           return "Unknown column"

       firstRow = next(spamreader)

       previousValue = firstRow[columnIndex]
       previousState = 'Straight'

       totalRows = transformedRows = 1
       for row in spamreader:
           totalRows+=1
           try:
               if row[columnIndex] > previousValue:
                   if previousState != 'Left':
                       transformedRows+=1
                       outputFile.write(previousState)
                   previousState = "Left"
               elif row[columnIndex] < previousValue:
                   if previousState != 'Right':
                       transformedRows+=1
                       outputFile.write(previousState)
                   previousState = "Right"
               elif row[columnIndex] == previousValue:
                   if previousState != 'Straight':
                       transformedRows+=1
                       outputFile.write(previousState)
                   previousState = "Straight"
               previousValue = row[columnIndex]
           except:
               continue

       return "Transformation Successful"

def sameValues(columnName):
    with open('../../Downloads/record(1).csv', 'rb') as inputFile , open('../../Downloads/_'+columnName+'_sameValues_record.csv', 'wb') as outputFile:
       spamreader = csv.reader(inputFile, delimiter=',')
       columnLabels = next(spamreader)

       try:
           columnIndex = columnLabels.index(columnName)
       except:
           return "Unknown column"

       previousValue = -1
       totalRows = transformedRows = 1
       for row in spamreader:
           totalRows+=1
           try:
               if row[columnIndex] != previousValue:
                   transformedRows+=1
                   outputFile.write(row[columnIndex])
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

        (direction = 0) if (first > previous) else (direction = 1)
        
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

                else previous > int(row[columnIndex]):
                    if direction == 0:
                        previous = int(row[columnIndex])
                        continue
                    else:
                        direction = 0
                        previous = int(row[columnIndex])
                        outFile.write("Increasing")

                else:
                    previous = int(row[columnIndex])

        print totalRows + "rows transformed."
        return "Transformation Successfull"


print definedMoves()
print sameValues("US_2")

'''
with open('../../Downloads/record.csv', 'rb') as csvfile:
   spamreader = csv.reader(csvfile, delimiter=',')
   row1 = next(spamreader)

   print row1.index('Timestamp')
   time.sleep(5)
   for row in spamreader:
        for item in row:
            temp.append(item.strip())
        
        print temp
        temp = []
        print '\n'
        time.sleep(1)
        '''
