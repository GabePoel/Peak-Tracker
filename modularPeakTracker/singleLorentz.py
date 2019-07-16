import numpy as np
import modularLiveFit as fit

class SingleLorentz:
    def __init__(self, dataBatch):
        self.localIndex = None
        self.dataBatch = dataBatch
        self.xBackgroundData = self.dataBatch.getData("all", None, "freq")
        self.yBackgroundData = self.dataBatch.getData("all", None, "r")
        self.peakFrequency = None
        self.amplitude = None
        self.skew = None
        self.fullWidthHalfMaximum = None
        self.hasBackground = False
        self.leftDistance = np.inf
        self.rightDistance = np.inf

    def setupData(self):
        localMin = self.peakFrequency - 2 * self.fullWidthHalfMaximum
        localMax = self.peakFrequency + 2 * self.fullWidthHalfMaximum
        self.minMax = (localMin, localMax)
        self.xData = self.dataBatch.getData(self.minMax, "point", "freq")
        self.yData = self.dataBatch.getData(self.minMax, "point", "r", "freq")
        self.localMin = localMin
        self.localMax = localMax
        self.dataTerms = {"freq": self.peakFrequency, "amp": self.amplitude, \
            "skew": self.skew, "width": self.fullWidthHalfMaximum}
    
    def getParameter(self, parameterType):
        return self.dataTerms[parameterType]

    def setSingleParameters(self, parameters, includeBackground=False):
        self.amplitude = parameters[0]
        self.skew = parameters[1]
        self.peakFrequency = parameters[2]
        self.fullWidthHalfMaximum = parameters[3]
        if includeBackground:
            self.hasBackground = True
            self.slope = parameters[4]
            self.offset = parameters[5]
        self.setupData()

    def getSingleParameters(self, includeBackground=False):
        parameters = np.array([])
        parameters = np.append(parameters, self.amplitude)
        parameters = np.append(parameters, self.skew)
        parameters = np.append(parameters, self.peakFrequency)
        parameters = np.append(parameters, self.fullWidthHalfMaximum)
        if includeBackground:
            parameters = np.append(parameters, self.slope)
            parameters = np.append(parameters, self.offset)
        return parameters

    def getSingleFit(self):
        xFitData = self.xData
        yFitData = fit.getFitData(self, xFitData)
        return xFitData, yFitData

    def setIndex(self, index):
        self.localIndex = index
