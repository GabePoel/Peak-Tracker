import numpy as np
import modularConfig as conf
from postDataBatch import PostDataBatch

class ModularFitTracker:
    def __init__(self, parent):
        self.parent = parent
        self.currentIndex = 1
        self.readyToAdjust = False
        self.dataSet = parent.dataSet
        self.preDataBuffer = parent.processedDataBuffer
        self.postDataBuffer = None
        self.totalDataBatches = len(self.dataSet.preDataBatchArray)
        self.fig = parent.fig
        self.ax = parent.ax
        self.canvas = parent.canvas
        self.minFrequency = self.dataSet.minFrequency
        self.maxFrequency = self.dataSet.maxFrequency
        self.track()
    
    def track(self):
        self.prepDataSet()

    def prepDataSet(self):
        for i in range(0, self.totalDataBatches):
            localMin = self.dataSet.getDataBatch(i).getData(None, "min", "freq")[0]
            localMax = self.dataSet.getDataBatch(i).getData(None, "max", "freq")[0]
            self.minFrequency = max(localMin, self.minFrequency)
            self.maxFrequency = min(localMax, self.maxFrequency)
        self.dataSet.minFrequency = self.minFrequency
        self.dataSet.maxFrequency = self.maxFrequency
        self.initializePostDataBatchArray()
        self.fitOverEveryDataBatch()

    def initializePostDataBatchArray(self):
        for preDataBatch in self.dataSet.preDataBatchArray:
            postDataBatch = PostDataBatch(self.dataSet)
            postDataBatch.inheritData(preDataBatch)
            self.dataSet.postDataBatchArray.append(postDataBatch)

    def fitOverEveryDataBatch(self):
        for i in range(0, self.totalDataBatches):
            self.currentIndex = i
            self.fitOverSingleDataBatch(i)
        self.parent.exportVideo()

    def fitOverSingleDataBatch(self, index, mode="automatic"):
        if index == 0:
            referenceDataBatch = self.preDataBuffer
        else:
            referenceDataBatch = self.dataSet.getDataBatch(index - 1, "pre")
        targetDataBatch = self.dataSet.getDataBatch(index, "post")
        targetDataBatch.clearLorentz()
        targetDataBatch.importLorentzFromDataBatch(referenceDataBatch)
        nextDataBatch = self.dataSet.getDataBatch(index, "pre")
        nextDataBatch.clearLorentz()
        nextDataBatch.importLorentzFromDataBatch(targetDataBatch)
        if conf.liveUpdate:
            self.plotDataBatch(targetDataBatch)
        if conf.exportImages:
            self.exportCurrentImage()

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
        self.canvas.draw()

    def exportCurrentImage(self):
        if conf.exportImages:
            frameNumber = str(self.currentIndex)
            numZeros = 5 - len(frameNumber)
            frameName = "frame" + ("0" * numZeros) + frameNumber
            self.parent.exportPlot(frameName)

    def adjustPreDataBuffer(self):
        if self.readyToAdjust:
            currentIndex = self.preDataBuffer.index
            currentTemperature = self.preDataBuffer.startTemp
            for i in range(max(0, currentIndex - 5), currentIndex):
                frequencyArray = self.getFrequencies(self.preDataBuffer)
                temperatureArray = self.getTemperature
        else:
            print("Not ready to adjust.")

    def getFrequencies(self, dataBatch):
        allParameters = dataBatch.getAllParameters()
        frequencyParameters = allParameters[2::4]
        return frequencyParameters