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
