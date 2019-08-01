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

class ModularApplication:
    def __init__(self):
        self.runningLog = "Running Log:\n\n"
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = None
        self.currentProgress = 0
        self.dataSet = None
        self.freshDataBuffer = None
        self.processedDataBuffer = None
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
        tdmsDirectory = os.path.join(self.importDirectory, "tdmsData")
        self.dataSet = ModularDataSet(tdmsDirectory)
        self.freshDataBuffer = self.dataSet.getDataBatch(0)
        x = self.freshDataBuffer.getData("all", None, "freq")
        y = self.freshDataBuffer.getData("all", None, "r")
        self.ax.plot(x, y)
        self.canvas.draw()

    def runTracker(self):
        if self.processedDataBuffer is None:
            print("No default data to track from")
        else:
            print("Ready to track")
            ModularFitTracker(self)

    def setExportDirectory(self, filePath):
        self.exportDirectory = filePath

    def setImportDirectory(self, filePath):
        self.importDirectory = filePath

    def setDataSet(self, dataSet):
        self.dataSet = dataSet

    def updateExportFolder(self, location="default"):
        exportLocation = self.exportDirectory
        if location != "default":
            exportLocation = location
        exportFolders = os.listdir(exportLocation)
        existingExportNumbers = []
        for folder in exportFolders:
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
    
    def loadSavedParameters(self, name="default", location="default", \
        index=0):
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

    def exportPlot(self, name):
        targetFolder = os.path.join(self.currentExportFolder, "exportImages")
        if not ("exportImages" in os.listdir(self.currentExportFolder)):
            os.makedirs(targetFolder)
        self.fig.savefig(targetFolder + "/" + str(name))

def loadDefaultImportDirectory():
    root = os.getcwd()
    importDirectory = os.path.join(root, "defaultImportDirectory")
    if conf.defaultImportDirectory != "default":
        importDirectory = conf.defaultImportDirectory
    return importDirectory

def loadDefaultExportDirectory():
    root = os.getcwd()
    exportDirectory = os.path.join(root, "defaultExportDirectory")
    if conf.defaultExportDirectory != "default":
        exportDirectory = conf.defaultExportDirectory
    return exportDirectory

def makeImageBuffer(imageDirectoryFilePath):
    imageBuffer = [image for image in os.listdir(imageDirectoryFilePath) \
        if image.endswith(".png")]
    imageBuffer.sort()
    return imageBuffer
