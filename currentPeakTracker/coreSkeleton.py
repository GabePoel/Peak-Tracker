#!/usr/bin/env python

import os
import glob
import numpy as np
import fitAction as fa
import dataManagement as dm
import guiVisualizer as gv
import matplotlib.pyplot as plt
from importlib import reload


class Skeleton:
    def __init__(self, window):
        self.directory = os.getcwd()
        self.initParamList = np.array([])
        self.filePaths = []
        self.totalMaxFreq = np.inf
        self.totalMinFreq = -np.inf
        self.process = True
        self.dataSets = []
        self.fit = None
        self.window = window
        self.fig = window.fig
        self.ax = window.ax

    def refresh(self):
        self.fig = self.window.fig
        self.ax = self.window.ax

    def startStop(self):
        self.process = not self.process

    def calibrateFiles(self):
        self.totalMaxFreq = np.inf
        self.totalMinFreq = -np.inf
        self.filePaths = []
        self.dataSets = []
        directories = [self.directory]
        for dir in directories:
            dir += "/"
            self.filePaths = self.filePaths + sorted(glob.glob(dir + "*.tdms"))
        for filePath in self.filePaths:
            self.dataSets = self.dataSets + [dm.getData(filePath)]
        for dataSet in self.dataSets:
            newMin, newMax = dm.getDataCriteria(dataSet, self.totalMaxFreq,
                                                self.totalMinFreq)
            self.totalMinFreq = newMin
            self.totalMaxFreq = newMax

    def processData(self):
        self.calibrateFiles()
        plt.ion()
        count = len(self.dataSets)
        self.window.updateCanvas()
        self.fit = fa.FitProcedure(self.totalMinFreq, self.totalMaxFreq,
                                   self.initParamList, self, count)
        print("self.initParamList:")
        print(self.initParamList)
        self.fit.trackPeaks(self.initParamList, self.filePaths)

    def restart(self):
        self.window._quitTracker()
        reload(fa)
        reload(dm)
        reload(gv)
        reload(plt)
        runVisualizer()


def runVisualizer():
    newWindow = gv.VisualizationWindow()
    newWindow.runWindow()
