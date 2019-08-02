import numpy as np
import modularLiveFit as fit
import modularConfig as conf

class SingleLorentz:
    def __init__(self, dataBatch):
        self.localIndex = dataBatch.lorentzCount
        self.dataBatch = dataBatch
        self.xBackgroundData = self.dataBatch.getData("all", None, "freq")
        self.yBackgroundData = self.dataBatch.getData("all", None, "r")
        self.peakFrequency = None
        self.amplitude = None
        self.skew = None
        self.fullWidthHalfMaximum = None
        self.hasBackground = False
        self.leftDistance = -np.inf
        self.rightDistance = np.inf
        self.trueLeft = None
        self.trueRight = None
        self.xData = None
        self.yData = None
        self.fitCost = None

    def initialSetup(self, amplitude, peakFrequency, fullWidthHalfMaximum, \
        skew):
        if peakFrequency is None or fullWidthHalfMaximum is None:
            self.peakFrequency = peakFrequency
            self.fullWidthHalfMaximum = fullWidthHalfMaximum
            self.skew = skew
            self.amplitude = amplitude
        else:
            self.updateAmplitude(amplitude)
            self.updatePeakFrequency(peakFrequency)
            self.updateSkew(skew)
            self.updateWidth(fullWidthHalfMaximum)
        self.setupData()

    def getID(self):
        dataBatchMessage = "[dataBatch: " + str(self.dataBatch.index) + ", "
        lorentzMessage = "lorentz: " + str(self.localIndex) + "]"
        return "ID: " + dataBatchMessage + lorentzMessage

    def copyLorentz(self, lorentz):
        self.peakFrequency = lorentz.peakFrequency
        self.amplitude = lorentz.amplitude
        self.skew = lorentz.skew
        self.fullWidthHalfMaximum = lorentz.fullWidthHalfMaximum
        self.setupData()

    def setupData(self):
        self.trueLeft = self.peakFrequency - \
            (self.fullWidthHalfMaximum * conf.multiFitLimit)
        self.trueRight = self.peakFrequency + \
            (self.fullWidthHalfMaximum * conf.multiFitLimit)
        self.dataFiltration(conf.widthExpansionBase)
        self.dataTerms = {"freq": self.peakFrequency, "amp": self.amplitude, \
            "skew": self.skew, "width": self.fullWidthHalfMaximum}

    def dataFiltration(self, growthLevel="default", growPower=0):
        if growthLevel == "default":
            growthLevel = conf.widthExpansionBase
        localMin = self.peakFrequency - \
            (growthLevel * self.fullWidthHalfMaximum) ** \
                (conf.widthExpansionRate * growPower)
        localMax = self.peakFrequency + \
            (growthLevel * self.fullWidthHalfMaximum) ** \
                (conf.widthExpansionRate * growPower)
        self.minMax = (localMin, localMax)
        self.xData = self.dataBatch.getData(self.minMax, "point", "freq")
        self.yData = self.dataBatch.getData(self.minMax, "point", "r", "freq")
        self.localMin = localMin
        self.localMax = localMax
        if len(self.xData) < 4:
            self.dataFiltration(growthLevel + 1, growPower + 1)

    def updateAmplitude(self, newAmplitude):
        self.amplitude = newAmplitude

    def updatePeakFrequency(self, newPeakFrequency):
        self.peakFrequency = newPeakFrequency
        self.setupData()

    def updateSkew(self, newSkew):
        self.skew = newSkew

    def updateWidth(self, newFullWidthHalfMaximum):
        self.fullWidthHalfMaximum = newFullWidthHalfMaximum
        self.setupData()
    
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
