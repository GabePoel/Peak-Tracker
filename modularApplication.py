from __future__ import division
import os
import cv2
import numpy as np
import modularConfig as conf
from dataBatch import DataBatch
from matplotlib.figure import Figure
from modularManualPeakDetector import ModularManualPeakDetector
from modularDataSet import ModularDataSet
from modularVisualizer import ModularVisualizer
from modularFitTracker import ModularFitTracker
from modularDataAnalyzer import ModularDataAnalyzer

class ModularApplication:
    def __init__(self):
        self.runningLog = "Running Log:\n\n"
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.startIndex = None
        self.endIndex = None
        self.readyForTracking = False
        self.canvas = None
        self.currentProgress = 0
        self.dataSet = None
        self.freshDataBuffer = None
        self.processedDataBuffer = None
        self.fullDataTable = None
        self.simpleDataTable = None
        self.cacheDirectory = loadDefaultCacheDirectory()
        self.importDirectory = loadDefaultImportDirectory()
        self.exportDirectory = loadDefaultExportDirectory()
        self.currentExportFolder = self.updateExportFolder()
        self.visualization = ModularVisualizer(self)

    def updateRunningLog(self, message, logID):
        if conf.allowedLogUpdates[logID]:
            self.runningLog += ("\n" + message)
            self.exportRunningLog()

    def detectPeaks(self, index=0):
        freshData = self.dataSet.getDataBatch(0)
        detection = ModularManualPeakDetector(self, freshData)
        self.processedDataBuffer = detection.getProcessedData()

    def loadDataSet(self):
        tdmsDirectory = self.importDirectory
        self.dataSet = ModularDataSet(tdmsDirectory)
        self.startIndex = self.setStartIndex()
        self.endIndex = self.setEndIndex()
        self.dataSet.truncateDataBatch(self.startIndex, self.endIndex)
        if conf.reverseTrackingOrder:
            self.dataSet.reverseDataBatch()
        self.freshDataBuffer = self.dataSet.getDataBatch(0)
        x = self.freshDataBuffer.getData("all", None, "freq")
        y = self.freshDataBuffer.getData("all", None, "r")
        self.ax.plot(x, y)
        self.canvas.draw()

    def setStartIndex(self):
        if conf.trackingStartValue == "start":
            return 0
        elif conf.trackingStartValue == "end":
            return self.dataSet.dataNumber
        else:
            return conf.trackingStartValue
    
    def setEndIndex(self):
        if conf.trackingEndValue == "start":
            endIndex = 0
        elif conf.trackingEndValue == "end":
            endIndex = self.dataSet.dataNumber
        else:
            endIndex = conf.trackingEndValue
        return max(self.startIndex, endIndex)

    def runTracker(self):
        if self.processedDataBuffer is None:
            print("No default data to track from")
        else:
            print("Ready to track")
            ModularFitTracker(self)

    def getDataResults(self):
        dataAnalyzer = ModularDataAnalyzer(self)
        self.fullDataTable = \
            dataAnalyzer.createFullDataTable(conf.dataExportHeaders)
        self.simpleDataTable = \
            dataAnalyzer.createSimpleDataTable(conf.dataExportHeaders)
        dataAnalyzer.plotDataTable()

    def setExportDirectory(self, filePath):
        self.exportDirectory = filePath
        self.currentExportFolder = self.updateExportFolder()

    def setImportDirectory(self, filePath):
        self.importDirectory = filePath
        print(self.cacheDirectory)
        importLocation = os.path.join(self.cacheDirectory, "importLocation.txt")
        importString = open(importLocation, 'w')
        importString.truncate(0)
        importString.write(filePath)
        importString.close()

    def setDataSet(self, dataSet):
        self.dataSet = dataSet

    def updateExportFolder(self, location="default"):
        exportLocation = self.exportDirectory
        if location != "default":
            exportLocation = location
        exportFolders = os.listdir(exportLocation)
        existingExportNumbers = []
        for folder in exportFolders:
            if folder.startswith('export'):
                try:
                    existingExportNumbers.append(int(folder[6:]))
                except:
                    pass
        if len(existingExportNumbers) == 0:
            thisExportNumber = 1
        else:
            thisExportNumber = max(existingExportNumbers) + 1
        newExportFolder = os.path.join(exportLocation, "export" + \
            str(thisExportNumber))
        os.makedirs(newExportFolder)
        return newExportFolder

    def quickDisplay(self):
        self.ax.cla()
        freq = self.freshDataBuffer.getData("all", None, "freq")
        r = self.freshDataBuffer.getData("all", None, "r")
        x = self.freshDataBuffer.getData("all", None, "x")
        y = self.freshDataBuffer.getData("all", None, "y")
        self.ax.plot(freq, r, color="r")
        self.ax.plot(freq, x, color="b")
        self.ax.plot(freq, y, color="g")
        self.canvas.draw()

    def saveCurrentParameters(self):
        parameterBuffer = self.freshDataBuffer.getAllParameters()
        self.exportParameters(parameterBuffer, location=self.importDirectory)
        self.exportParameters(parameterBuffer, location=self.cacheDirectory)

    def loadSavedParameters(self, name="default", location="default", \
        index=0):
        if self.readyForTracking:
            self.loadDataSet()
        self.readyForTracking = True
        importLocation = self.importDirectory
        importName = 'parameterExport.csv'
        if location != "default":
            importLocation = location
        if name != "default":
            importName = name
        importFilePath = os.path.join(importLocation, importName)
        parameters = np.genfromtxt(importFilePath, delimiter=",")
        freshData = self.dataSet.getDataBatch(index)
        detection = ModularManualPeakDetector(self, freshData)
        detection.importParameters(parameters)

    def exportDataTable(self, dataBuffer="default", name="default", \
        location="default"):
        exportLocation = location
        exportName = name
        exportData = dataBuffer
        if location == "default":
            exportLocation = self.currentExportFolder
        if name == "default":
            exportName = "lorentzExport"
        if dataBuffer == "default":
            exportData = self.fullDataTable
            simpleExportData = self.simpleDataTable
        if conf.exportDataComplex:
            targetFolder = os.path.join(exportLocation, "exportLorentzians")
            if not ("exportLorentzians" in os.listdir(exportLocation)):
                os.makedirs(targetFolder)
            decimals = len(str(len(exportData)))
            for i in range(0, len(exportData)):
                numZeros = decimals - len(str(i))
                lorentzName = exportName + ("0" * numZeros) + str(i) + ".csv"
                exportFilePath = os.path.join(targetFolder, lorentzName)
                np.savetxt(exportFilePath, exportData[i], delimiter=",", \
                    fmt='%s')
        if conf.exportDataSimple:
            exportFilePath = os.path.join(exportLocation, \
                'frequencyResultsExport.csv')
            np.savetxt(exportFilePath, self.simpleDataTable, delimiter=",", \
                fmt='%s')

    def exportParameters(self, parameterBuffer="default", name="default", \
        location="default"):
        exportLocation = self.currentExportFolder
        exportName = 'parameterExport.csv'
        if parameterBuffer == "default":
            parameterBuffer = self.freshDataBuffer.getAllParameters()
        if location != "default":
            exportLocation = location
        if name != "default":
            exportName = name
        exportFilePath = os.path.join(exportLocation, exportName)
        np.savetxt(exportFilePath, parameterBuffer, delimiter=",")

    def exportRunningLog(self, name="default", location="default"):
        exportLocation = location
        exportName = name
        if location == "default":
            exportLocation = self.currentExportFolder
        if name == "default":
            exportName = "runningLog.txt"
        writeLocation = os.path.join(exportLocation, exportName)
        writeFile = open(writeLocation, mode='w')
        writeFile.write(self.runningLog)
        writeFile.close()

    def circlePreview(self):
        self.ax.cla()
        x = self.freshDataBuffer.getData("all", None, "x")
        y = self.freshDataBuffer.getData("all", None, "y")
        self.ax.plot(x, y)
        self.canvas.draw()

    def circlePreviewWithLorentz(self):
        self.ax.cla()
        x = self.freshDataBuffer.getData("all", None, "x")
        y = self.freshDataBuffer.getData("all", None, "y")

    def exportConfig(self, name="default", location="default"):
        root = os.getcwd()
        exportFolder = self.currentExportFolder
        exportName = 'configExport.txt'
        if location != "default":
            exportFolder = location
        if name != "default":
            exportName = name
        writeFilePath = os.path.join(exportFolder, exportName)
        writeFile = open(writeFilePath, mode='w')
        configFilePath = os.path.join(root, 'modularConfig.py')
        configFile = open(configFilePath, mode='r')
        configContent = configFile.read()
        configFile.close()
        writeFile.write(configContent)
        writeFile.close()

    def exportVideo(self, imageBuffer="default", name="default", \
        location="default"):
        imageLocation = os.path.join(self.currentExportFolder, "exportImages")
        if imageBuffer == "default":
            imageBuffer = makeImageBuffer(imageLocation)
        exportLocation = self.currentExportFolder
        exportName = 'videoExport.avi'
        if location != "default":
            exportLocation = location
        if exportName != "default":
            exportName = name
        videoExport = os.path.join(exportLocation, 'videoExport.avi')
        frame = cv2.imread(os.path.join(imageLocation, imageBuffer[0]))
        height, width, layers = frame.shape
        video = cv2.VideoWriter(videoExport, 0, 1, (width, height))
        for image in imageBuffer:
            frame = cv2.imread(os.path.join(imageLocation, image))
            video.write(frame)
        video.release()
        cv2.destroyAllWindows()

    def exportPlot(self, name, location="default"):
        if location == "default":
            targetFolder = os.path.join(self.currentExportFolder, "exportImages")
            if not ("exportImages" in os.listdir(self.currentExportFolder)):
                os.makedirs(targetFolder)
        else:
            targetFolder = location
        exportFileName = os.path.join(targetFolder, str(name))
        self.fig.savefig(exportFileName)

def loadDefaultCacheDirectory():
    root = os.getcwd()
    cacheDirectory = os.path.join(root, "workingCache")
    print(cacheDirectory)
    return cacheDirectory

def loadDefaultImportDirectory():
    if conf.quickLoadDirectory:
        cacheDirectory = loadDefaultCacheDirectory()
        importLocation = os.path.join(cacheDirectory, "importLocation.txt")
        importString = open(importLocation, 'r')
        importDirectory = importString.read()
        importString.close()
    else:
        root = os.getcwd()
        importDirectory = os.path.join(root, "defaultImportDirectory/tdmsData")
        if conf.defaultImportDirectory != "default":
            importDirectory = conf.defaultImportDirectory
    return importDirectory

def loadDefaultExportDirectory():
    root = os.getcwd()
    exportDirectory = os.path.join(root, "defaultExportDirectory")
    if conf.defaultExportDirectory == "local":
        exportDirectory = os.path.expanduser('~/Documents')
        if not ("Peak Tracker Exports" in os.listdir(exportDirectory)):
            os.makedirs(os.path.join(exportDirectory, "Peak Tracker Exports"))
        exportDirectory = os.path.join(exportDirectory, "Peak Tracker Exports")
    elif conf.defaultExportDirectory != "default":
        exportDirectory = conf.defaultExportDirectory
    return exportDirectory

def makeImageBuffer(imageDirectoryFilePath):
    imageBuffer = [image for image in os.listdir(imageDirectoryFilePath) \
        if image.endswith(".png")]
    imageBuffer.sort()
    return imageBuffer
