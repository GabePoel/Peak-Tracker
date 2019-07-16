from __future__ import division
import os
import cv2
import numpy as np
import modularConfig as mc
from matplotlib.figure import Figure
from modularManualPeakDetector import ModularManualPeakDetector
from modularDataSet import ModularDataSet
from modularVisualizer import ModularVisualizer
from modularFitTracker import ModularFitTracker

class ModularApplication:
    def __init__(self):
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

    def detectPeaks(self, index=0):
        freshData = self.dataSet.getDataBatch(index)
        detection = ModularManualPeakDetector(self, freshData)
        self.processedDataBuffer = detection.getProcessedData()

    def loadDataSet(self):
        self.dataSet = ModularDataSet(self.importDirectory)
        self.freshDataBuffer = self.dataSet.getDataBatch(0)
        x = self.freshDataBuffer.getData("all", None, "freq")
        y = self.freshDataBuffer.getData("all", None, "r")
        self.ax.plot(x, y)
        self.canvas.draw()

    def runTracker(self):
        if self.processedDataBuffer is None:
            print("No default data to track from.")
        else:
            print("Ready to track.")
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
            existingExportNumbers.append(int(folder[6:]))
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

    def exportParameters(self, parameterBuffer, name="deafult", \
        location="default"):
        exportLocation = self.currentExportFolder
        exportName = 'parameterExport.csv'
        if location != "default":
            exportLocation = location
        if name != "default":
            exportName = name
        exportFilePath = os.path.join(exportLocation, exportName)
        np.savetxt(exportFilePath, parameterBuffer, delimiter=",")

    def circlePreview(self):
        self.ax.cla()
        x = self.freshDataBuffer.getData("all", None, "x")
        y = self.freshDataBuffer.getData("all", None, "y")
        self.ax.plot(x, y)
        self.canvas.draw()

    # def circlePreviewWithLorentz(self):
    #     self.ax.cla()
    #     x = self.freshDataBuffer.getData("all", None, "x")
    #     y = self.freshDataBuffer.getData("all", None, "x")
    #     for lorentz in self.freshDataBuffer.lorentzArray:
    #         frequencySubset = 

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

    def exportVideo(self, imageBuffer, name="default", location="default"):
        exportLocation = self.currentExportFolder
        exportName = 'videoExport.avi'
        if location != "default":
            exportLocation = location
        if exportName != "default":
            exportName = name
        videoExport = os.path.join(exportLocation, 'videoExport.avi')
        frame = cv2.imread(os.path.join(location, imageBuffer[0]))
        height, width, layers = frame.shape
        video = cv2.VideoWriter(videoExport, 0, 1, (width, height))
        for image in imageBuffer:
            frame = cv2.imread(os.path.join(location, image))
            video.write(frame)
        video.release()
        cv2.destroyAllWindows()

def loadDefaultImportDirectory():
    root = os.getcwd()
    importDirectory = os.path.join(root, "defaultImportDirectory")
    if mc.defaultImportDirectory != "default":
        importDirectory = mc.defaultImportDirectory
    return importDirectory

def loadDefaultExportDirectory():
    root = os.getcwd()
    exportDirectory = os.path.join(root, "defaultExportDirectory")
    if mc.defaultExportDirectory != "default":
        exportDirectory = mc.defaultExportDirectory
    return exportDirectory

def makeImageBuffer(imageDirectoryFilePath):
    imageBuffer = [image for image in os.listdir(imageDirectoryFilePath) \
        if image.endswith(".png")]
    return imageBuffer
