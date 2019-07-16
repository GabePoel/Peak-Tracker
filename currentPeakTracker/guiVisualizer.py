#!/usr/bin/env python

import coreUtils as cu
import coreSkeleton as cs
import dataManagement as dm
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from tkinter import *


class VisualizationWindow:
    def __init__(self, master=None):
        self.root = Tk()
        self.root.wm_title("Live Peak Tracker Visualizer")
        self.controls = Frame(self.root)
        self.controls.pack(side="top", fill="both", expand=True)

        O = Button(master=self.root, text="Select",
                   command=self._selectDirectory)
        S = Button(master=self.root, text="Detect",
                   command=self._detectPeaks)
        P = Button(master=self.root, text="Track",
                   command=self._track)
        D = Button(master=self.root, text="Load",
                   command=self._demoPlot)
        G = Button(master=self.root, text="Save",
                   command=self._getData)
        Q = Button(master=self.root, text="Quit",
                   command=self._quitTracker)
        R = Button(master=self.root, text="Refresh",
                   command=self._reloadTracker)
        S.pack(in_=self.controls, side="left")
        P.pack(in_=self.controls, side="left")
        Q.pack(in_=self.controls, side="left")
        O.pack(in_=self.controls, side="left")
        D.pack(in_=self.controls, side="left")
        G.pack(in_=self.controls, side="left")
        R.pack(in_=self.controls, side="left")
        self.hasPeaks = False
        self.fig, self.ax = plt.subplots()
        self.skeleton = cs.Skeleton(self)
        self.counter = 0
        self.exportDirectory = cu.getExportDirectory()

        self.prepWindow()

    def prepWindow(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="bottom", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack()

    def _quitTracker(self):
        self.root.quit()
        self.root.destroy()

    def _reloadTracker(self):
        self.skeleton.restart()

    def _selectDirectory(self, targetDir=None):
        if not targetDir:
            Tk().withdraw()
            self.skeleton.directory = filedialog.askdirectory()
        else:
            self.skeleton.directory = targetDir
        self.skeleton.calibrateFiles()
        initData = dm.getData(self.skeleton.filePaths[0])
        [freq, X, Y, startTemp, endTemp] = initData.peakPlotParams()
        R = initData.R
        self.fig, self.ax = plt.subplots()
        plt.plot(freq, R, picker=5)
        self.updateCanvas()

    def _detectPeaks(self, givenPeaks=None):
        self.hasPeaks = True
        self.detection = cu.prepPeaks(self.skeleton, givenPeaks)
        self.skeleton.initParamList = self.detection.getParams()
        print("detected/updated initParamList:")
        print(self.skeleton.initParamList)

    def _track(self):
        self.skeleton.initParamList = self.detection.getParams()
        self.skeleton.processData()

    def _getData(self):
        if self.hasPeaks:
            self.skeleton.initParamList = self.detection.getParams()
            print(self.skeleton.initParamList)
            np.savetxt("exportParams.csv", self.skeleton.initParamList,
                       delimiter=",")
        else:
            print("We do not have any peaks.")

    def _demoPlot(self):
        dir = cu.demoPlot()
        print("Directory targeted: +" + str(dir))
        self._selectDirectory(dir)
        givenPeaks = np.genfromtxt('exportParams.csv', delimiter=",")
        print('givenPeaks:')
        print(givenPeaks)
        self._detectPeaks(givenPeaks)

    def savePlot(self, name, countBool):
        if countBool:
            ct = str(self.counter)
            counter = ('0' * (4 - len(ct))) + ct
        else:
            counter = ""
        self.fig.savefig(self.exportDirectory + '/' + str(name) +
                         str(counter) + '.png')
        self.counter += 1

    def saveVid(self):
        cu.exportVideo(self.exportDirectory)

    def updateCanvas(self):
        self.canvas._tkcanvas.pack_forget()
        self.toolbar.pack_forget()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="bottom", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack()
        self.skeleton.refresh()

    def quickUpdate(self):
        self.canvas.draw()

    def quickPause(self, interval):
        time.sleep(0.05)

    def runWindow(self):
        mainloop()
