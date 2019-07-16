import copy
import glob
import numpy as np
from preDataBatch import PreDataBatch
from postDataBatch import PostDataBatch

class ModularDataSet:
    def __init__(self, directory):
        self.dataNumber = 0
        self.preDataBatchArray = []
        self.postDataBatchArray = []
        self.minFrequency = -np.inf
        self.maxFrequency = np.inf
        self.importFromDirectory(directory)

    def sortData(self):
        dataBuffer = sorted(self.preDataBatchArray, key=lambda data: data.startTemp)
        for i in range(0, self.dataNumber):
            self.preDataBatchArray[i] = dataBuffer[i]
            self.preDataBatchArray[i].setIndex(i)

    def importFromDirectory(self, directory):
        filePaths = sorted(glob.glob(directory + "/*.tdms"))
        for filePath in filePaths:
            self.importFile(filePath)

    def importFile(self, filePath):
        dataBatch = PreDataBatch(self)
        dataBatch.loadData(filePath)
        dataBatch.setIndex(self.dataNumber)
        self.preDataBatchArray.append(dataBatch)
        self.dataNumber += 1

    def importData(self, dataBatch):
        dataBatch.setIndex(self.dataNumber)
        self.preDataBatchArray.append(dataBatch)
        self.dataNumber += 1

    def importDataSet(self, dataSet):
        newDataArray = copy.copy(dataSet.preDataBatchArray)
        newProcessedArray = copy.copy(dataSet.postDataBatchArray)
        for i in range(0, dataSet.dataNumber):
            newDataArray.setIndex(self.dataNumber)
            newProcessedArray.setIndex(self.dataNumber)
            self.dataNumber += 1
        self.preDataBatchArray += newDataArray

    def getDataBatch(self, index, batch="pre"):
        if batch == "pre":
            return self.preDataBatchArray[index]
        elif batch == "post":
            return self.postDataBatchArray[index]
        else:
            return self.preDataBatchArray[index]