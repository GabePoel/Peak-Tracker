from matplotlib.widgets import RectangleSelector
from matplotlib.widgets import Cursor
import coreUtils as cu
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
    plt.ion()


    def rectSelectCallback(eclick, erelease):
        print("running rectSelectCallback")
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
        return


    def confirmSelection(event):
        print("running confirmSelection")
        global enableSelection
        if event.key in ['enter'] and enableSelection:
            confirmSelection.RS.set_active(False)
            enableSelection = False
            fig.canvas.mpl_disconnect(cid1)
            fig.canvas.mpl_disconnect(cid2)
            print("disconnection confirmed")
            return


    def firstPoint(event):
        print("running firstPoint")
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
        return


    cursor = Cursor(ax, useblit = True, color = '0.5', linewidth = 1,
                    linestyle = ':')
    confirmSelection.RS = RectangleSelector(ax, rectSelectCallback,
                                            drawtype = 'box', useblit = True,
                                            button = [3], minspanx = 5,
                                            minspany = 5, spancoords = 'pixels',
                                            interactive = True)


    cid1 = fig.canvas.mpl_connect('key_press_event', confirmSelection)
    cid2 = fig.canvas.mpl_connect('pick_event', firstPoint)
    print("second disconnect confirmation")
    while enableSelection:
        plt.pause(0.001)
        print("pausing...")
    params = np.array([])
    for i in range(0, min(savedWidths.shape[0], savedFrequencies.shape[0])):
        a = savedAmplitudes[i]
        s = -savedAmplitudes[i]
        f = savedFrequencies[i]
        w = savedWidths[i]
        newParams = [a, s, f, w]
        params = np.append(params, newParams)
        params = cu.paramSort(params)
    return params
