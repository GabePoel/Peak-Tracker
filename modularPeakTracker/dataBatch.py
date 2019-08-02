import os
import numpy as np
import modularConfig as conf
import modularLiveFit as fit
from nptdms import TdmsFile
from singleLorentz import SingleLorentz

class DataBatch:
    '''
    The primary storage method for a batch of data associated with a
    particular temperature.
    '''

    def __init__(self, parent):
        self.parent = parent
        self.index = None
        self.lorentzArray = []
        self.lorentzCount = 0
        self.freqData = None
        self.rData = None
        self.dataCount = 0
        self.searchTerms = {"freq": self.freqData, "r": self.rData}
        self.startTemp = None
        self.endTemp = None
        self.date = None
        self.filePath = None
        self.xData = None
        self.yData = None
        self.cryoData = None
        self.colorFreqData = None
        self.startTempVec = None
        self.additionalSetup()

    def getSingleParameterList(self, parameterType):
        '''
        Returns a list containing numpy arrays of the Lorentzian parameters.
        '''
        singleParameterList = []
        for lorentz in self.lorentzArray:
            singleParameterList.append(lorentz.getParameter(parameterType))
        return singleParameterList

    def searchTerm(self, dataType=None):
        '''
        Finds the data or value associated with the specific search term which
        should be inputed as a string.
        '''
        if dataType is None:
            return self.freqData
        else:
            return self.searchTerms[dataType]

    def searchDataPoint(self, val, dataType=None):
        '''
        Searches the array associated with the specified data type for the
        value that best matches the input one specified.
        '''
        dataArray = self.searchTerm(dataType)
        dataArray = np.abs(dataArray - val)
        index = dataArray.argmin()
        return index

    def searchDataPoints(self, vals, dataType=None):
        '''
        Searches the array associated with the specified data type for the
        values that best match the input array specified.
        '''
        vals = vals.tolist()
        indexes = []
        for val in vals:
            indexes.append(self.searchDataPoint(val, dataType))
        return np.array(indexes).astype(int)

    def getData(self, ref=None, guide=None, outType=None, refType=None):
        '''
        Takes in all sorts of inputs and returns either a numpy array of data
        values or specific doubles of those values themselves based on input.
        The shortcut keys for getData are as specified below:
        '''
        targetArray = self.searchTerm(outType)
        if guide == "min":
            dataMin = 0
            dataMax = dataMin + 1
        elif guide == "max":
            dataMin = self.dataCount - 1
            dataMax = dataMin + 1
        elif ref == "local":
            firstLorentz = self.lorentzArray[0]
            lastLorentz = self.lorentzArray[self.lorentzCount - 1]
            extraSpace = max(self.getSingleParameterList("width"))
            leftFrequency = firstLorentz.localMin - extraSpace
            rightFrequency = lastLorentz.localMax + extraSpace
            ref = (leftFrequency, rightFrequency)
            return self.getData(ref, "point", outType, "freq")
        elif guide == "array":
            indices = self.searchDataPoints(ref, refType)
            return targetArray[indices]
        elif (ref is None) or (guide is None) or (ref == "all"):
            guide = "index"
            dataMin = 0
            dataMax = self.dataCount - 1
        else:
            guide = "point"
            if refType is None:
                refType = outType
            dataMin = self.searchDataPoint(ref[0], refType)
            dataMax = self.searchDataPoint(ref[1], refType)
        return targetArray[dataMin:dataMax]

    def addLorentz(self, singleLorentz):
        singleLorentz.setIndex(self.lorentzCount)
        self.lorentzArray.append(singleLorentz)
        self.lorentzCount += 1
        return singleLorentz

    def addNewLorentz(self):
        singleLorentz = SingleLorentz(self)
        return self.addLorentz(singleLorentz)

    def sortLorentz(self):
        lorentzBuffer = sorted(self.lorentzArray, key=lambda lorentz: \
            lorentz.peakFrequency)
        for i in range(0, self.lorentzCount):
            self.lorentzArray[i] = lorentzBuffer[i]
            self.lorentzArray[i].setIndex(i)

    def getLorentz(self, index):
        return self.lorentzArray[index]

    def updateLorentzDistances(self):
        self.sortLorentz()
        for i in range(1, self.lorentzCount):
            thisPosition = self.lorentzArray[i].peakFrequency
            lastPosition = self.lorentzArray[i - 1].peakFrequency
            self.lorentzArray[i].leftDistance = thisPosition - lastPosition
        for i in range(0, self.lorentzCount - 1):
            thisPosition = self.lorentzArray[i].peakFrequency
            nextPosition = self.lorentzArray[i + 1].peakFrequency
            self.lorentzArray[i].rightDistance = nextPosition - thisPosition

    def clearLorentz(self):
        self.lorentzArray = []
        self.lorentzCount = 0

    def hasLorentz(self):
        if self.lorentzCount > 0:
            return True
        return False

    def getAllParameters(self, includeBackground=False):
        allParameters = np.array([])
        for lorentz in self.lorentzArray:
            allParameters = np.append(allParameters, \
                lorentz.getSingleParameters(includeBackground))
        return allParameters

    def groupLorentz(self):
        if self.lorentzCount == 1:
            lorentzSets = [(0,)]
        elif self.lorentzCount == 0:
            lorentzSets = []
        else:
            lorentzSets = []
            for lorentz in self.lorentzArray:
                lorentzSets.append(set([lorentz.localIndex]))
            for i in range(1, self.lorentzCount):
                leftLorentz = self.lorentzArray[i - 1]
                rightLorentz = self.lorentzArray[i]
                leftMax = leftLorentz.trueRight
                rightMin = rightLorentz.trueLeft
                if leftMax >= rightMin:
                    lorentzSets[i - 1] |= lorentzSets[i]
                    lorentzSets[i] = lorentzSets[i - 1]
            for i in range(0, len(lorentzSets)):
                lorentzSets[i] = list(lorentzSets[i])
                lorentzSets[i].sort()
                lorentzSets[i] = tuple(lorentzSets[i])
        lorentzSets = set(lorentzSets)
        lorentzSets = list(lorentzSets)
        lorentzSets = sorted(lorentzSets, key=lambda set: set[0])
        return lorentzSets

    def getMultiParameters(self):
        self.sortLorentz()
        lorentzSets = self.groupLorentz()
        parameterList = []
        for i in range(0, len(lorentzSets)):
            parameters = np.array([])
            for j in lorentzSets[i]:
                parameters = np.append(parameters, \
                    self.lorentzArray[j].getSingleParameters())
            parameterList.append(parameters)
        return parameterList

    def getSplitParameters(self):
        multiParamaterList = self.getMultiParameters
        return self.splitParameterList(multiParamaterList)

    def getMultiFit(self):
        return fit.getMultiFitData(self)

    def setIndex(self, index):
        self.index = index

    def getPeakPositions(self):
        peakPositions = []
        self.sortLorentz()
        for lorentz in self.lorentzArray:
            peakPositions.append(lorentz.peakFrequency)
        return peakPositions

    def fitLorentz(self):
        parameterList = fit.getMultiFitParameterList(self)
        self.clearLorentz()
        self.importLorentzFromParameterList(parameterList)

    def importLorentzFromParameterList(self, parameterList):
        parameterList = self.splitParameterList(parameterList)
        for parameters in parameterList:
            lorentz = SingleLorentz(self)
            lorentz.setSingleParameters(parameters)
            self.addLorentz(lorentz)
        self.sortLorentz()

    def importLorentzFromParameters(self, parameters):
        self.importLorentzFromParameterList([parameters])

    def splitParameterList(self, parameterList):
        splitParameters = []
        for parameters in parameterList:
            if len(parameters) > 4:
                splitParameters += np.split(parameters, len(parameters) / 4)
            else:
                splitParameters.append(parameters)
        return splitParameters

    def importLorentzFromLorentzArray(self, lorentzArray):
        for oldLorentz in lorentzArray:
            oldParameters = oldLorentz.getSingleParameters()
            newLorentz = SingleLorentz(self)
            newLorentz.setSingleParameters(oldParameters)
            self.addLorentz(newLorentz)
        self.sortLorentz()

    def importLorentzFromDataBatch(self, dataBatch):
        for lorentz in dataBatch.lorentzArray:
            newLorentz = self.addNewLorentz()
            newLorentz.copyLorentz(lorentz)

    def inheritData(self, dataBatch):
            self.freqData = dataBatch.freqData
            self.rData = dataBatch.rData
            self.startTemp = dataBatch.startTemp
            self.endTemp = dataBatch.endTemp
            self.searchTerms["freq"] = self.freqData
            self.searchTerms["r"] = self.rData
            self.setIndex(dataBatch.index)

    def additionalSetup(self):
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
        self.startTemp = self.cryoData[0]
        self.endTemp = self.cryoData[-1]
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

    def copyDataBatch(self, dataBatch):
        self.inheritData(dataBatch)
        self.importLorentzFromDataBatch(dataBatch)
        self.refreshSearch()

def interpolateNans(inputArray):
    if np.isnan(inputArray).any():
        boolArray = ~np.isnan(inputArray)
        goodIndices = boolArray.nonzero()[0]
        goodPoints = inputArray[~np.isnan(inputArray)]
        badIndices = np.isnan(inputArray).nonzero()[0]
        inputArray[np.isnan(inputArray)] = \
            np.interp(badIndices, goodIndices, goodPoints)
    return inputArray

