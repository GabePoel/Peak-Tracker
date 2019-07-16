#!/usr/bin/env python

from matplotlib.widgets import RectangleSelector
from matplotlib.widgets import Cursor
import coreUtils as cu
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class GivenPeakSelection:
    def __init__(self, detection):
        self.detection = detection

    def getParams(self):
        return self.detection


class ManualPeakSelection:
    def __init__(self, skeleton):
        self.savedRectangles = np.empty(shape=[0, 4])
        self.savedFrequencies = np.array([])
        self.savedAmplitudes = np.array([])
        self.savedWidths = np.array([])
        self.rectList = []
        self.enableSelection = True
        self.skeleton = skeleton
        fig = skeleton.fig
        ax = skeleton.ax
        self.runSelection(fig, ax)

    def rectSelectCallback(self, eclick, erelease):
        print("running rectSelectCallback")
        selectBalance = self.savedWidths.shape[0] - self.savedFrequencies.shape[0]
        if self.enableSelection and selectBalance < 1:
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata
            xDis = np.abs(x1 - x2)
            yDis = np.abs(y1 - y2)
            x0 = min(x1, x2)
            y0 = min(y1, y2)
            self.savedWidths = np.append(self.savedWidths, [xDis])
            self.savedAmplitudes = np.append(self.savedAmplitudes, [yDis])
            rect = patches.Rectangle((x0, y0), xDis, yDis, linewidth=1,
                                     edgecolor='r', linestyle='--',
                                     facecolor='none')
            rect2 = patches.Rectangle((x0, y0), xDis, yDis, linewidth=1,
                                      edgecolor='g', linestyle='--',
                                      facecolor='none')
            self.rectList.append(rect2)
            self.ax.add_patch(rect)
            plt.draw()
        return

    def confirmSelection(self, event):
        print("running confirmSelection")
        print(event.key)
        if event.key in ['enter'] and self.enableSelection:
            self.RS.set_active(False)
            self.enableSelection = False
            self.fig.canvas.mpl_disconnect(self.cid1)
            self.fig.canvas.mpl_disconnect(self.cid2)
            for rect in self.rectList:
                self.ax.add_patch(rect)
            plt.draw()
            print("disconnection confirmed")

    def firstPoint(self, event):
        print("running firstPoint")
        selectBalance = self.savedWidths.shape[0] - self.savedFrequencies.shape[0]
        if self.enableSelection and selectBalance > -1:
            thisClick = event.artist
            xData = thisClick.get_xdata()
            yData = thisClick.get_ydata()
            ind = event.ind
            plt.plot(xData[ind][0], yData[ind][0], 'x', color='r')
            self.savedFrequencies = np.append(self.savedFrequencies,
                                              xData[ind][0])
            self.fig.canvas.draw()
        return

    def getParams(self):
        params = np.array([])
        for i in range(0, min(self.savedWidths.shape[0],
                              self.savedFrequencies.shape[0])):
            a = self.savedAmplitudes[i]
            s = -self.savedAmplitudes[i]
            f = self.savedFrequencies[i]
            w = self.savedWidths[i] / 2
            newParams = [a, s, f, w]
            params = np.append(params, newParams)
            params = cu.paramSort(params)
        return params

    def runSelection(self, fig, ax):
        self.fig = fig
        self.ax = ax
        plt.ion()
        self.cursor = Cursor(ax, useblit=True, color='0.5', linewidth=1,
                             linestyle=':')
        self.RS = RectangleSelector(self.ax, self.rectSelectCallback,
                                    drawtype='box', useblit=True,
                                    button=[3], minspanx=5,
                                    minspany=5, spancoords='pixels',
                                    interactive=True)

        self.cid1 = fig.canvas.mpl_connect('key_press_event',
                                           self.confirmSelection)
        self.cid2 = fig.canvas.mpl_connect('pick_event', self.firstPoint)
        plt.ion()
