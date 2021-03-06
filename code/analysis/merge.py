import os
import csv
import sys
import copy

def getMin(dataList):
    column1 = []
    pos = []
    
    for f in dataList:
        column1.append(f.split(',')[0])
        for x in column1:
            if x != '':
                min_ = int(x)
                pos.append(column1.index(x))
                break
    
    for x in column1:
        if x.isdigit():
            try:
                if int(x)<min_:
                    min_ = int(x)
                    if column1.index(x) not in pos:
                        pos.append(column1.index(x))
            except Exception as e:
                    print e
    return pos

def getList(dataList):
    column1 = []
  
    column1.append(dataList[0].split(',')[0])
    for f in dataList:
            column1.append(f.split(',')[1].strip("\r\n"))
    return column1
    

def mergeFiles(outFileName,fileList):
    with open(outFileName+'.csv','w') as outputFile:
        spamOutput = csv.writer(outputFile, delimiter=',')

        count = len(fileList)
        dataList = []
        dataListCopy = []
        fileObjectList = []

        for i in range(count):
            fileObjectList.append(open("transformations/toMerge/"+fileList[i],'r'))
            dataList.append(fileObjectList[i].readline())

        dataListCopy = copy.copy(dataList)
        while 1:
            notEmptyCount = sum(map(lambda i:0 if i=='' else 1 , dataList))
            if notEmptyCount==0:
                print dataList
                print dataListCopy
                for f in fileObjectList:
                    f.close()
                break
            
            pos = getMin(dataList)

            if not pos:
                print "No More Data"
                sys.exit()
            #emptyList = map(lambda i:"",range(pos-1))

            row = getList(dataListCopy)
            print "dataList Row ",row
            print "pos = ",pos
            row[0] = dataList[pos[0]].split(',')[0]

            print "Data List copy row ", row
            spamOutput.writerow(row)

            for i in pos:
                dataList[i] = fileObjectList[i].readline()
                if dataList[i]!='':
                    dataListCopy[i] = dataList[i]


def getFileList():
    return os.listdir('./transformations/toMerge')


outFileName = sys.argv[1]
#fileList = sys.argv[2].split(" ")

fileList = getFileList()

print outFileName
print fileList

mergeFiles(outFileName, fileList)
