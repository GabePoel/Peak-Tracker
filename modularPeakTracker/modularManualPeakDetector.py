import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import RectangleSelector
from matplotlib.widgets import Cursor
from matplotlib.colors import to_hex
from preDataBatch import PreDataBatch
from postDataBatch import PostDataBatch
from preSingleLorentz import PreSingleLorentz

class ModularManualPeakDetector:
    def __init__(self, parent, preDataBatch):
        self.savedSelectionBuffer = None
        self.savedSelection = []
        self.savedSelectionCount = 0
        self.cidPress = None
        self.cidPick = None
        self.cidSelect = None
        self.lastAction = None
        self.fitPoints = None
        self.preDataBatch = preDataBatch
        self.postDataBatch = None
        self.processedData = None
        self.rectList = []
        self.allowedActions = ["pick", "select"]
        self.done = False
        self.parent = parent
        self.fig = parent.fig
        self.ax = parent.ax
        self.canvas = parent.canvas
        self.setupPeakDetector()

    def __call__(self, event):
        return

    def setupPeakDetector(self):
        freqData = self.preDataBatch.getData("all", None, "freq")
        rData = self.preDataBatch.getData("all", None, "r")
        self.ax.cla()
        self.ax.plot(freqData, rData, picker=5, color='595959')
        self.cursor = Cursor(self.ax, useblit=True, color='0.5', \
            linewidth=1, linestyle=":")
        self.canvas.draw()
        self.ax.autoscale(enable=False)

    def connect(self):
        self.cidPress = \
            self.fig.canvas.mpl_connect('key_press_event', self.onPress)
        self.cidPick = \
            self.fig.canvas.mpl_connect('pick_event', self.onPick)
        self.cidSelect = RectangleSelector(self.ax, self.onSelect, \
            drawtype='box', useblit=True, button=[3], minspanx=5, \
            minspany=5, spancoords='pixels', interactive=True)

    def onPick(self, event):
        if "pick" in self.allowedActions:
            self.lastAction = "pick"
            ind = event.ind
            pressData = event.artist
            xPnt = pressData.get_xdata()[ind][0]
            yPnt = pressData.get_ydata()[ind][0]
            rect = self.getRect()
            rect.xPnt = xPnt
            rect.yPnt = yPnt
            rect.hasPoint = True
            self.plotRect(rect, 'r')
            self.canvas.draw()
            self.removeAction("pick")
            if "select" in self.allowedActions:
                self.allowedActions = ["select", "cancel", "restart"]
            else:
                self.allowedActions = ["cancel", "comit", "restart"]

    def onSelect(self, eclick, erelease):
        if "select" in self.allowedActions:
            self.lastAction = "select"
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata
            xDis = np.abs(x1 - x2)
            yDis = np.abs(y1 - y2)
            xPos = min(x1, x2)
            yPos = min(y1, y2)
            rect = self.getRect()
            rect.xDis = xDis
            rect.yDis = yDis
            rect.xPos = xPos
            rect.yPos = yPos
            rect.hasSelection = True
            self.plotRect(rect, 'r')
            self.canvas.draw()
            self.removeAction("select")
            if "pick" in self.allowedActions:
                self.allowedActions = ["pick", "cancel", "restart"]
            else:
                self.allowedActions = ["cancel", "comit", "restart"]

    def onPress(self, event):
        self.actionFilter()
        if event.key == ' ' and "comit" in self.allowedActions:
            self.lastAction = "comit"
            self.comitSelection(self.savedSelectionBuffer)
            self.savedSelectionBuffer = None
            self.canvas.draw()
            self.allowedActions = ["pick", "select", "delete", "finish", \
                "restart"]
        elif event.key == 'backspace' and "cancel" in self.allowedActions:
            self.lastAction = "cancel"
            rect = self.savedSelectionBuffer
            self.cancelSelection(rect)
            self.canvas.draw()
            self.savedSelectionBuffer = None
            self.allowedActions = ["pick", "select", "delete", "finish", \
                "restart"]
        elif event.key == 'backspace' and "delete" in self.allowedActions:
            self.lastAction = "delete"
            rect = self.savedSelection.pop()
            self.cancelSelection(rect)
            self.savedSelectionCount -= 1
            self.canvas.draw()
            self.allowedActions = ["pick", "select", "delete", "finish", \
                "restart"]
        elif event.key == 'enter' and "finish" in self.allowedActions:
            self.lastAction = "finish"
            rect = self.savedSelectionBuffer
            if rect is not None:
                self.cancelSelection(rect)
            self.canvas.draw()
            self.savedSelectionBuffer = None
            self.allowedActions = []
            self.processedData = self.preDataBatch
            self.done = True
            self.canvas.mpl_disconnect(self.cidPick)
            self.canvas.mpl_disconnect(self.cidPress)
            self.canvas.mpl_disconnect(self.cidSelect)
            self.parent.processedDataBuffer = self.processedData
            self.parent.runTracker()
        elif event.key == 'escape' and "restart" in self.allowedActions:
            self.lastAction = "restart"
            while self.savedSelectionCount > 0:
                rect = self.savedSelection.pop()
                self.cancelSelection(rect)
                self.savedSelectionCount -= 1
            self.canvas.draw()
            self.allowedActions = ["pick", "select"]
        elif event.key == 'q':
            print("savedSelectionBuffer: " + str(self.savedSelectionBuffer))
        elif event.key == 'w':
            print("allowedActions: " + str(self.allowedActions))
        elif event.key == 'e':
            print("savedSelection: " + str(self.savedSelection) + "   count: " \
            + str(self.savedSelectionCount))
        elif event.key == 'r':
            print("lastAction: " + str(self.lastAction))

    def actionFilter(self):
        if self.savedSelectionCount == 0:
            self.removeAction("delete")
            self.removeAction("finish")
        if self.savedSelectionBuffer is None:
            self.removeAction("comit")

    def getRect(self):
        if self.savedSelectionBuffer is None:
            self.savedSelectionBuffer = GivenSelection()
        return self.savedSelectionBuffer

    def comitSelection(self, rect):
        if rect not in self.savedSelection:
            rect.makeSingleLorentz(self.preDataBatch)
            self.savedSelection.append(rect)
            self.savedSelectionCount += 1
            self.plotRect(rect, 'g')
            self.totalFitPlot('g')

    def cancelSelection(self, rect):
        if rect.patch is not None:
            rect.patch.remove()
        if rect.points is not None:
            for point in rect.points:
                point.remove()
        if rect.plot is not None:
            for point in rect.plot:
                point.remove()
        self.clearFitPoints()
        self.totalFitPlot('g')

    def getProcessedData(self):
        self.connect()
        return self.processedData

    def removeAction(self, action):
        if action in self.allowedActions:
            self.allowedActions.remove(action)

    def plotRect(self, rect, setColor='r'):
        if rect.patch is not None:
            rect.patch.remove()
        if rect.points is not None:
            for point in rect.points:
                point.remove()
        if rect.hasSelection:
            rect.patch = patches.Rectangle((rect.xPos, rect.yPos), rect.xDis, \
                rect.yDis, linewidth=1, edgecolor=setColor, linestyle='--', \
                facecolor='none')
            self.ax.add_patch(rect.patch)
        if rect.hasPoint:
            rect.points = self.ax.plot(rect.xPnt, rect.yPnt, 'x', \
                color=setColor)

    def totalFitPlot(self, setColor='r'):
        self.preDataBatch.clearLorentz()
        self.clearFitPoints()
        for rect in self.savedSelection:
            if rect.hasLorentz:
                self.preDataBatch.addLorentz(rect.singleLorentz)
        if self.preDataBatch.hasLorentz():
            fitList = self.preDataBatch.getMultiFit()
            for fit in fitList:
                self.addToFitPoints(self.ax.plot(fit[0], fit[1], \
                    color=setColor))

    def clearFitPoints(self):
        if self.fitPoints is not None:
            while len(self.fitPoints) > 0:
                line = self.fitPoints.pop()
                line.remove()
            self.fitPoints = None

    def addToFitPoints(self, points):
        if self.fitPoints is None:
            self.fitPoints = points
        else:
            self.fitPoints += points

class GivenSelection:
    def __init__(self):
        self.xDis = None
        self.yDis = None
        self.xPos = None
        self.yPos = None
        self.xPnt = None
        self.yPnt = None
        self.hasSelection = False
        self.hasPoint = False
        self.hasLorentz = False
        self.patch = None
        self.points = None
        self.plot = None
        self.singleLorentz = None

    def makeSingleLorentz(self, dataBatch):
        self.singleLorentz = PreSingleLorentz(dataBatch)
        self.singleLorentz.amplitude = self.yDis
        self.singleLorentz.skew = -self.singleLorentz.amplitude
        self.singleLorentz.peakFrequency = self.xPnt
        self.singleLorentz.fullWidthHalfMaximum = self.xDis / 2
        self.singleLorentz.setupData()
        self.hasLorentz = True
