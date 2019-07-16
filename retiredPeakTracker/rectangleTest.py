from matplotlib.widgets import RectangleSelector
from matplotlib.widgets import Cursor
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


savedRectangles = np.empty(shape = [0, 4])
savedFrequencies = np.array([])
savedAmplitudes = np.array([])
savedWidths = np.array([])
enableSelection = True


def manualPeakSelection(fig, ax):
    global savedRectangles
    global savedFrequencies
    global savedAmplitudes
    global savedWidths
    global enableSelection
    savedRectangles = np.empty(shape = [0, 4])
    savedFrequencies = np.array([])
    savedAmplitudes = np.array([])
    savedWidths = np.array([])
    enableSelection = True


    def rectSelectCallback(eclick, erelease):
        global savedFrequencies
        global savedRectangles
        global savedWidths
        global savedAmplitudes
        global enableSelection
        selectBalance = savedWidths.shape[0] - savedFrequencies.shape[0]
        print (savedWidths)
        print (savedFrequencies)
        print (selectBalance)
        if enableSelection and selectBalance < 1:
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata
            thisRect = np.array([[x1, y1, x2, y2]])
            savedRectangles = np.append(savedRectangles, thisRect, axis = 0)
            xDis = np.abs(x1 - x2)
            yDis = np.abs(y1 - y2)
            x0 = min(x1, x2)
            y0 = min(y1, y2)
            savedWidths = np.append(savedWidths, [xDis])
            savedAmplitudes = np.append(savedAmplitudes, [yDis])
            rect = patches.Rectangle((x0, y0), xDis, yDis, linewidth = 1,
                                     edgecolor = 'r', linestyle = '--',
                                     facecolor = 'none')
            ax.add_patch(rect)
            plt.draw()


    def confirmSelection(event):
        global enableSelection
        global cid1
        global cid2
        if event.key in ['enter'] and enableSelection:
            confirmSelection.RS.set_active(False)
            enableSelection = False
            fig.canvas.mpl_disconnect(cid1)
            fig.canvas.mpl_disconnect(cid2)


    def firstPoint(event):
        global savedFrequencies
        global savedWidths
        global enableSelection
        selectBalance = savedWidths.shape[0] - savedFrequencies.shape[0]
        print (savedWidths)
        print (savedFrequencies)
        print (selectBalance)
        if enableSelection and selectBalance > -1:
            thisClick = event.artist
            xData = thisClick.get_xdata()
            yData = thisClick.get_ydata()
            ind = event.ind
            plt.plot(xData[ind][0], yData[ind][0], 'x', color = 'r')
            savedFrequencies = np.append(savedFrequencies, xData[ind][0])
            fig.canvas.draw()


    cursor = Cursor(ax, useblit = True, color = '0.5', linewidth = 1, linestyle = ':')
    confirmSelection.RS = RectangleSelector(ax, rectSelectCallback,
                                            drawtype = 'box', useblit = True,
                                            button = [3], minspanx = 5,
                                            minspany = 5, spancoords = 'pixels',
                                            interactive = True)


    cid1 = fig.canvas.mpl_connect('key_press_event', confirmSelection)
    cid2 = fig.canvas.mpl_connect('pick_event', firstPoint)
    while enableSelection:
        plt.pause(0.001)
    params = np.array([])
    for i in range(0, min(savedWidths.shape[0], savedFrequencies.shape[0])):
        a = savedAmplitudes[i]
        s = -savedAmplitudes[i]
        f = savedFrequencies[i]
        w = savedWidths[i]
        newParams = [a, s, f, w]
        params = np.append(params, newParams)
    return params


t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)


fig, ax = plt.subplots()
plt.plot(t, s, picker = 5)
print(manualPeakSelection(fig, ax))
