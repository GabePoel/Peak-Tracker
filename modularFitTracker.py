import numpy as np
import modularConfig as conf
import modularLiveFit as fit
import trackingUtilities as util
from singleLorentz import SingleLorentz
from dataBatch import DataBatch
from scipy.signal import savgol_filter

class ModularFitTracker:
    def __init__(self, parent):
        self.parent = parent
        self.currentIndex = 1
        self.dataSet = parent.dataSet
        self.preDataBuffer = parent.processedDataBuffer
        self.totalDataBatches = len(self.dataSet.dataBatchArray)
        if conf.quickTracking:
            self.totalDataBatches = conf.quickTrackingLength
            self.dataSet.dataNumber = conf.quickTrackingLength
            self.dataSet.dataBatchArray = self.dataSet.dataBatchArray[0:\
                conf.quickTrackingLength]
        self.fig = parent.fig
        self.ax = parent.ax
        self.canvas = parent.canvas
        self.minFrequency = self.dataSet.minFrequency
        self.maxFrequency = self.dataSet.maxFrequency
        self.typicalLorentz = None
        self.noiseLevel = None
        self.track()

    def track(self):
        self.prepDataSet()
        self.fitOverEveryDataBatch()
        self.parent.getDataResults()
        self.parent.exportVideo()
        self.parent.exportConfig()
        self.parent.exportRunningLog()
        self.parent.exportParameters()
        self.parent.exportDataTable()
        if conf.exportFinalTrends:
            self.parent.exportPlot("results", self.parent.currentExportFolder)

    def prepDataSet(self):
        self.noiseLevel = util.noisePredictor(self.dataSet.getDataBatch(0))
        for i in range(0, self.totalDataBatches):
            localMin = self.dataSet.getDataBatch(i).getData(None, "min", "freq")[0]
            localMax = self.dataSet.getDataBatch(i).getData(None, "max", "freq")[0]
            self.minFrequency = max(localMin, self.minFrequency)
            self.maxFrequency = min(localMax, self.maxFrequency)
        self.dataSet.minFrequency = self.minFrequency
        self.dataSet.maxFrequency = self.maxFrequency

    def fitOverEveryDataBatch(self):
        for i in range(1, self.totalDataBatches):
            self.currentIndex = i
            self.fitOverSingleDataBatch(i)
        print("Done with the fitting.")

    def fitOverSingleDataBatch(self, index, mode="automatic"):
        referenceDataBatch, targetDataBatch = \
            self.getDataBatchesForIndex(index)
        targetDataBatch.fitLorentz()
        targetDataBatch = self.correctTargetDataBatch(referenceDataBatch, \
            targetDataBatch)
        if conf.liveUpdate:
            self.plotDataBatch(targetDataBatch)
        if conf.exportImages:
            self.exportCurrentImage()
        log = "Lorentz Costs:"
        for lorentz in targetDataBatch.lorentzArray:
            log += " - " + str(lorentz.fitCost)
        self.parent.updateRunningLog(log, "COST_LOG")

    def predictReferenceDataBatch(self, dataBatch):
        if conf.rateOfChangeTracking:
            if self.currentIndex == 0:
                return dataBatch
            else:
                for lorentz in dataBatch.lorentzArray:
                    lorentz = self.predictNewLorentz(lorentz)
                return dataBatch
        else:
            return dataBatch

    def predictNewLorentz(self, lorentz):
        endIndex = self.currentIndex
        if endIndex < 2:
            return lorentz
        else:
            maxIndexSearch = min(endIndex, conf.rateOfChangeLength)
            previousAmplitudes = np.array([])
            previousFrequencies = np.array([])
            previousSkews = np.array([])
            previousWidths = np.array([])
            for i in range(endIndex - maxIndexSearch, endIndex):
                specificLorentz = self.getLorentz(i, lorentz.localIndex)
                specificAmplitude = specificLorentz.amplitude
                specificFrequency = specificLorentz.peakFrequency
                specificSkew = specificLorentz.skew
                specificWidth = specificLorentz.fullWidthHalfMaximum
                previousAmplitudes = np.append(previousAmplitudes, \
                    specificAmplitude)
                previousFrequencies = np.append(previousFrequencies, \
                    specificFrequency)
                previousSkews = np.append(previousSkews, specificSkew)
                previousWidths = np.append(previousWidths, specificWidth)
            amplitudeDifferences = np.diff(previousAmplitudes)
            frequencyDifferences = np.diff(previousFrequencies)
            skewDifferences = np.diff(previousSkews)
            widthDifferences = np.diff(previousWidths)
            expectedAmplitudeDifference = np.mean(amplitudeDifferences)
            expectedFrequencyDifference = np.mean(frequencyDifferences)
            expectedSkewDifference = np.mean(skewDifferences)
            expectedWidthDifference = np.mean(widthDifferences)
            newAmplitude = expectedAmplitudeDifference + lorentz.amplitude
            newFrequency = expectedFrequencyDifference + lorentz.peakFrequency
            newSkew = expectedSkewDifference + lorentz.skew
            newWidth = expectedWidthDifference + lorentz.fullWidthHalfMaximum
            log = "CURRENT LORENTZ: " + lorentz.getID()
            log += "\nAMPLITUDES"
            log += "\n- previousAmplitudes: " + str(previousAmplitudes)
            log += "\n- amplitudeDifferences: " + str(amplitudeDifferences)
            log += "\n- expectedAmplitudeDifference: " + str(expectedAmplitudeDifference)
            log += "\nFREQUENCIES"
            log += "\n- previousFrequencies: " + str(previousFrequencies)
            log += "\n- frequencyDifferences: " + str(frequencyDifferences)
            log += "\n- expectedFrequencyDifference: " + str(expectedFrequencyDifference)
            log += "\nSKEWS"
            log += "\n- previousSkews: " + str(previousSkews)
            log += "\n- skewDifferences: " + str(skewDifferences)
            log += "\n- expectedSkewDifferences: " + str(expectedSkewDifference)
            log += "\nWIDTHS"
            log += "\n- previousWidths: " + str(previousWidths)
            log += "\n- widthDifferences: " + str(widthDifferences)
            log += "\n- expectedWidthDifference: " + str(expectedWidthDifference)
            self.parent.updateRunningLog(log, "RATE_OF_CHANGE_PREDICTION")
            lorentz.updateAmplitude(newAmplitude)
            lorentz.updatePeakFrequency(newFrequency)
            lorentz.updateSkew(newSkew)
            lorentz.updateWidth(newWidth)
            return lorentz

    def correctTargetDataBatch(self, referenceDataBatch, targetDataBatch):
        referenceLorentzArray = referenceDataBatch.lorentzArray
        targetLorentzArray = targetDataBatch.lorentzArray
        lorentzPairList = util.makeLorentzPairs(referenceLorentzArray, \
            targetLorentzArray)
        for pair in lorentzPairList:
            self.correctSingleLorentz(pair[0], pair[1])
        self.correctLorentzDegeneracies(targetLorentzArray)
        return targetDataBatch

    def correctLorentzDegeneracies(self, lorentzArray):
        for i in range(1, len(lorentzArray)):
            if lorentzArray[i] is None or lorentzArray[i - 1] is None:
                pass
            elif self.checkCloseLorentz(lorentzArray[i], lorentzArray[i - 1]):
                lastLorentz = lorentzArray[i - 1]
                thisLorentz = lorentzArray[i]
                lastFit = lastLorentz.getSingleFit()[1]
                thisFit = thisLorentz.getSingleFit()[1]
                lastLorentzFrequency = lastLorentz.peakFrequency
                thisLorentzFrequency = thisLorentz.peakFrequency
                frequencyCheck = (lastLorentzFrequency == thisLorentzFrequency)
                if lastFit.shape == thisFit.shape:
                    fitCheck = any(np.equal(lastFit, thisFit))
                    logOne = "Possible degeneracy at " + lastLorentz.getID()
                    logTwo = " and at " + thisLorentz.getID()
                    self.parent.updateRunningLog(logOne + logTwo, \
                        "DEGENERACY_LOG")
                else:
                    fitCheck = False
                if frequencyCheck or fitCheck:
                    thisLorentz.copyLorentz(lastLorentz)

    def correctSingleLorentz(self, referenceLorentz, targetLorentz):
        if not (referenceLorentz is None or targetLorentz is None):
            self.correctSingleLorentzWidth(referenceLorentz, targetLorentz)
            self.correctSingleLorentzAmplitude(referenceLorentz, targetLorentz)
            
    def correctSingleLorentzWidth(self, referenceLorentz, targetLorentz):
        referenceWidth = referenceLorentz.fullWidthHalfMaximum
        targetWidth = targetLorentz.fullWidthHalfMaximum
        widthGrow = (targetWidth > conf.widthGrowLimit * referenceWidth)
        widthShrink = (referenceWidth > conf.widthShrinkLimit * targetWidth)
        if widthGrow or widthShrink:
            logMessage = "Width correction at " + targetLorentz.getID()
            self.parent.updateRunningLog(logMessage, "WIDTH_CORRECTION")
            # targetLorentz.updatePeakFrequency(referenceLorentz.peakFrequency)
            targetLorentz.updateWidth(referenceWidth)
            targetLorentz.updateAmplitude(referenceLorentz.amplitude)
            targetLorentz.updateSkew(referenceLorentz.skew)
            
    def correctSingleLorentzAmplitude(self, referenceLorentz, targetLorentz):
        referenceAmplitude = referenceLorentz.amplitude
        targetAmplitude = targetLorentz.amplitude
        amplitudeGrowAmount = targetAmplitude / referenceAmplitude
        amplitudeShrinkAmount = referenceAmplitude / targetAmplitude
        amplitudeGrow = (conf.amplitudeGrowLimit < amplitudeGrowAmount)
        amplitudeShrink = (conf.amplitudeShrinkLimit < amplitudeShrinkAmount)
        amplitudeCutoff = (targetAmplitude < 2 * self.noiseLevel)
        if any([amplitudeGrow, amplitudeShrink]):
            logMessage = "Amplitude correction at " + targetLorentz.getID()
            self.parent.updateRunningLog(logMessage, "AMPLITUDE_CORRECTION")
            targetLorentz.updateAmplitude(referenceAmplitude)
            targetLorentz.updateSkew(referenceLorentz.skew)
            targetLorentz.updateWidth(referenceLorentz.fullWidthHalfMaximum)
        if amplitudeCutoff:
            logMessage = "Amplitude cutoff at " + targetLorentz.getID()
            self.parent.updateRunningLog(logMessage, "AMPLITUDE_CORRECTION")
            targetLorentz.updateAmplitude(referenceAmplitude)
            targetLorentz.updatePeakFrequency(referenceLorentz.peakFrequency)
            targetLorentz.updateSkew(referenceLorentz.skew)
            targetLorentz.updateWidth(referenceLorentz.fullWidthHalfMaximum)

    def checkCloseLorentz(self, lorentzOne, lorentzTwo):
        shortLorentzList = util.sortLorentzList([lorentzOne, lorentzTwo])
        lorentzOne = shortLorentzList[0]
        lorentzTwo = shortLorentzList[1]
        widthOne = lorentzOne.fullWidthHalfMaximum
        widthTwo = lorentzTwo.fullWidthHalfMaximum
        frequencyOne = lorentzOne.peakFrequency
        frequencyTwo = lorentzTwo.peakFrequency
        amplitudeOne = lorentzOne.amplitude
        amplitudeTwo = lorentzTwo.amplitude
        skewOne = lorentzOne.skew
        skewTwo = lorentzTwo.skew
        widthDifference = max(widthOne / widthTwo, widthTwo / widthOne)
        amplitudeDifference = max(amplitudeOne / amplitudeTwo, amplitudeTwo / \
            amplitudeOne)
        skewDifference = max(skewOne / skewTwo, skewTwo / skewOne)
        frequencySeparation = frequencyTwo - frequencyOne
        frequencyDifference = min(frequencySeparation / widthOne, \
            frequencySeparation / widthTwo)
        widthCheck = (widthDifference < conf.closeLorentzWidth) and \
            widthDifference > 1
        amplitudeCheck = (amplitudeDifference < conf.closeLorentzAmplitude) and \
            amplitudeDifference > 1
        skewCheck = (skewDifference < conf.closeLorentzSkew) and \
            skewDifference > 1
        frequencyCheck = (frequencyDifference < conf.closeLorentzFrequency)
        close = all([widthCheck, amplitudeCheck, frequencyCheck, skewCheck])
        if any([widthCheck, amplitudeCheck, frequencyCheck, skewCheck]):
            log = "Possible degeneracy at " + lorentzOne.getID()
            log += ", " + lorentzTwo.getID()
            log += "\n- widthDifference: " + str(widthDifference)
            log += "\n- - widthOne: " + str(widthOne)
            log += "\n- - widthTwo: " + str(widthTwo)
            log += "\n- amplitudeDifference: " + str(amplitudeDifference)
            log += "\n- - amplitudeOne: " + str(amplitudeOne)
            log += "\n- - amplitudeTwo: " + str(amplitudeTwo)
            log += "\n- skewDifference: " + str(skewDifference)
            log += "\n- - skewOne: " + str(skewOne)
            log += "\n- - skewTwo: " + str(skewTwo)
            log += "\n- frequencyDifference: " + str(frequencyDifference)
            log += "\n- - frequencyOne: " + str(frequencyOne)
            log += "\n- - frequencyTwo: " + str(frequencyTwo)
            log += "\n- - frequencySeparation: " + str(frequencySeparation)
            self.parent.updateRunningLog(log, "RATE_OF_CHANGE_PREDICTION")
        return close

    def getDataBatchesForIndex(self, index):
        targetDataBatch = self.dataSet.dataBatchArray[index]
        if index == 0:
            referenceDataBatch = self.preDataBuffer
            previousDataBatch = self.preDataBuffer
            targetDataBatch.importLorentzFromDataBatch(previousDataBatch)
        else:
            previousDataBatch = self.dataSet.dataBatchArray[index - 1]
            targetDataBatch.importLorentzFromDataBatch(previousDataBatch)
            self.predictReferenceDataBatch(targetDataBatch)
            referenceDataBatch = DataBatch(self.dataSet)
            referenceDataBatch.copyDataBatch(targetDataBatch)
        return referenceDataBatch, targetDataBatch

    def plotDataBatch(self, dataBatch):
        if conf.displayScale == "local":
            xBackground = dataBatch.getData("local", None, "freq")
            yBackground = dataBatch.getData("local", None, "r")
        else:
            xBackground = dataBatch.getData("all", None, "freq")
            yBackground = dataBatch.getData("all", None, "r")
        xPeaks = np.array(dataBatch.getSingleParameterList("freq"))
        yPeaks = dataBatch.getData(xPeaks, "array", "r", "freq")
        fitList = dataBatch.getMultiFit()
        self.ax.cla()
        self.ax.plot(xBackground, yBackground, color='b')
        for fit in fitList:
            self.ax.plot(fit[0], fit[1], color='r')
        self.ax.plot(xPeaks, yPeaks, 'x', color='g')
        if conf.noiseFilterDisplay:
            ySmooth = savgol_filter(yBackground, 53, 3)
            self.ax.plot(xBackground, ySmooth + self.noiseLevel, color='y')
            self.ax.plot(xBackground, ySmooth - self.noiseLevel, color='y')
        self.canvas.draw()

    def exportCurrentImage(self):
        if conf.exportImages:
            decimals = len(str(self.totalDataBatches))
            frameNumber = str(self.currentIndex)
            numZeros = decimals - len(frameNumber)
            frameName = "frame" + ("0" * numZeros) + frameNumber
            self.parent.exportPlot(frameName)

    def getLorentz(self, index, localIndex, type="post"):
        searchDataBatch = self.dataSet.getDataBatch(index, type)
        searchLorentz = searchDataBatch.lorentzArray[localIndex]
        return searchLorentz

    def fullBackgroundFit(self, dataBatch):
        pass
