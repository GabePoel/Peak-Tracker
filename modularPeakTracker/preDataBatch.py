import os
import numpy as np
from nptdms import TdmsFile
from dataBatch import DataBatch

class PreDataBatch(DataBatch):
    def additionalSetup(self):
        self.filePath = None
        self.xData = None
        self.yData = None
        self.cryoData = None
        self.colorFreqData = None
        self.startTempVec = None
        self.searchTerms['x'] = self.xData
        self.searchTerms['y'] = self.yData
        self.searchTerms['cryo'] = self.cryoData
        self.searchTerms['color'] = self.colorFreqData

    def loadData(self, filePath, cleanBool=True):
        fileName, ext = os.path.splitext(os.path.basename(filePath))
        tdmsFile = TdmsFile(filePath)
        date, time, startTemp, endTemp = fileName.split("_")
        self.startTemp = float(startTemp[:-1])
        self.endTemp = float(endTemp[:-1])
        self.ext = ext
        self.date = date
        self.time = time
        self.freqData = tdmsFile.object('Untitled', 'freq (Hz)').data
        self.xData = tdmsFile.object('Untitled', 'X1 (V)').data
        self.yData = tdmsFile.object('Untitled', 'Y1 (V)').data
        self.cryoData = tdmsFile.object('Untitled', 'Cryostat temp (K)').data
        if cleanBool == True:
            fullSignal = np.stack((self.freqData, self.xData, self.yData))
            cleanSignal = fullSignal[:, ~np.isnan(fullSignal).any(axis=0)]
            self.freqData = cleanSignal[0]
            self.xData = cleanSignal[1]
            self.yData = cleanSignal[2]
        else:
            self.xData = interpolateNans(self.xData)
            self.yData = interpolateNans(self.yData)
            self.freqData = interpolateNans(self.freqData)
        self.rData = np.sqrt(self.xData ** 2 + self.yData ** 2)
        self.startTempVec = self.startTemp * np.ones(len(self.rData))
        self.colorFreqData = self.freqData / 1000
        self.dataCount = len(self.freqData)
        self.refreshSearch()

    def refreshSearch(self):
        self.searchTerms['freq'] = self.freqData
        self.searchTerms['r'] = self.rData
        self.searchTerms['x'] = self.xData
        self.searchTerms['y'] = self.yData
        self.searchTerms['cryo'] = self.cryoData
        self.searchTerms['color'] = self.colorFreqData

def interpolateNans(inputArray):
    if np.isnan(inputArray).any():
        boolArray = ~np.isnan(inputArray)
        goodIndices = boolArray.nonzero()[0]
        goodPoints = inputArray[~np.isnan(inputArray)]
        badIndices = np.isnan(inputArray).nonzero()[0]
        inputArray[np.isnan(inputArray)] = \
            np.interp(badIndices, goodIndices, goodPoints)
    return inputArray
