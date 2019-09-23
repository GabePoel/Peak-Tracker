import copy
import glob
import numpy as np
from dataBatch import DataBatch

class ModularDataSet:
    def __init__(self, directory):
        self.dataNumber = 0
        self.dataBatchArray = []
        self.minFrequency = -np.inf
        self.maxFrequency = np.inf
        self.importFromDirectory(directory)

    def sortData(self):
        dataBuffer = sorted(self.dataBatchArray, key=lambda data: data.startTemp)
        for i in range(0, self.dataNumber):
            self.dataBatchArray[i] = dataBuffer[i]
            self.dataBatchArray[i].setIndex(i)

    def importFromDirectory(self, directory):
        filePaths = sorted(glob.glob(directory + "/*.tdms"))
        for filePath in filePaths:
            self.importFile(filePath)

    def importFile(self, filePath):
        dataBatch = DataBatch(self)
        dataBatch.loadData(filePath)
        dataBatch.setIndex(self.dataNumber)
        self.dataBatchArray.append(dataBatch)
        self.dataNumber += 1

    def importData(self, dataBatch):
        dataBatch.setIndex(self.dataNumber)
        self.dataBatchArray.append(dataBatch)
        self.dataNumber += 1

    def importDataSet(self, dataSet):
        newDataArray = copy.copy(dataSet.dataBatchArray)
        newProcessedArray = copy.copy(dataSet.dataBatchArray)
        for i in range(0, dataSet.dataNumber):
            newDataArray.setIndex(self.dataNumber)
            newProcessedArray.setIndex(self.dataNumber)
            self.dataNumber += 1
        self.dataBatchArray += newDataArray

    def getDataBatch(self, index, batch="pre"):
        if batch == "pre":
            returnDataBatch = self.dataBatchArray[index]
        elif batch == "post":
            returnDataBatch = self.dataBatchArray[index]
        else:
            returnDataBatch = self.dataBatchArray[index]
        returnDataBatch.index = index
        return returnDataBatch

    def truncateDataBatch(self, startIndex, endIndex):
        endIndex = max(startIndex, endIndex)
        self.dataBatchArray = self.dataBatchArray[startIndex:endIndex]
        self.dataNumber = endIndex - startIndex

    def reverseDataBatch(self):
        self.dataBatchArray = self.dataBatchArray[::-1]