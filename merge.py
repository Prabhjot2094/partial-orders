import os
import csv
import sys

def getMin(dataList):
    column1 = []
    
    for f in dataList:
        column1.append(f.split(',')[0])

	print column1
	for x in column1:
		if x.isdigit():
			min_ = int(x)
			pos = column1.index(x)
			break
    
    for x in column1:
		if x.isdigit():
			try:
				if int(x)<min_:
					min_ = int(x)
					pos = column1.index(x)
			except Exception as e:
				print e
	
    return pos

def mergeFiles(outFileName,fileList):
    with open(outFileName+'.csv','w') as outputFile:
        spamOutput = csv.writer(outputFile, delimiter=',')

        count = len(fileList)
        dataList = []
        fileObjectList = []

        for i in range(count):
            fileObjectList.append(open("transformations/"+fileList[i],'r'))
            dataList.append(fileObjectList[i].readline())

        while 1:
            notEmptyCount = sum(map(lambda i:0 if i=='' else 1 , dataList))
            if notEmptyCount==0:
                print notEmptyCount
                print dataList
                for f in fileObjectList:
                    f.close()
                break
            
            pos = getMin(dataList)

            row = dataList[pos].split(',')
            row[-1] = row[-1].strip("\r\n")
            spamOutput.writerow(row)
            dataList[pos] = fileObjectList[pos].readline()


outFileName = sys.argv[1]
fileList = sys.argv[2].split(" ")

print outFileName
print fileList

mergeFiles(outFileName, fileList)
