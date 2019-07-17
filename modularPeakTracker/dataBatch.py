import numpy as np
import modularConfig as mc
import modularLiveFit as fit
from singleLorentz import SingleLorentz

class DataBatch:
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
        self.additionalSetup()

    def additionalSetup(self):
        return

    def getSingleParameterList(self, parameterType):
        singleParameterList = []
        for lorentz in self.lorentzArray:
            singleParameterList.append(lorentz.getParameter(parameterType))
        return singleParameterList

    def searchTerm(self, dataType=None):
        if dataType is None:
            return self.freqData
        else:
            return self.searchTerms[dataType]

    def searchDataPoint(self, val, dataType=None):
        dataArray = self.searchTerm(dataType)
        dataArray = np.abs(dataArray - val)
        index = dataArray.argmin()
        return index

    def searchDataPoints(self, vals, dataType=None):
        vals = vals.tolist()
        indexes = []
        for val in vals:
            indexes.append(self.searchDataPoint(val, dataType))
        return np.array(indexes).astype(int)

    def getData(self, ref=None, guide=None, outType=None, refType=None):
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
        self.sortLorentz()

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
                leftMax = max(leftLorentz.xData)
                rightMin = min(rightLorentz.xData)
                if leftMax >= rightMin:
                    lorentzSets[i - 1] |= lorentzSets[i]
                    lorentzSets[i] = lorentzSets[i - 1]
            for i in range(0, len(lorentzSets)):
                lorentzSets[i] = list(lorentzSets[i])
                lorentzSets[i].sort()
                lorentzSets[i] = tuple(lorentzSets[i])
        lorentzSets = set(lorentzSets)
        lorentzSets = list(lorentzSets)
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

    def importLorentzFromParameterList(self, parameterList):
        parameterList = self.splitParameterList(parameterList)
        for parameters in parameterList:
            lorentz = SingleLorentz(self)
            lorentz.setSingleParameters(parameters)
            self.addLorentz(lorentz)
        self.sortLorentz()

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
        parameterList = fit.getMultiFitParameterList(dataBatch)
        self.importLorentzFromParameterList(parameterList)

