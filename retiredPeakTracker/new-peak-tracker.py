from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import time as wait
import math
import glob
import os

from numpy import sqrt
from nptdms import TdmsFile
from scipy import signal
from scipy.optimize import least_squares
from scipy.optimize import leastsq
from peakdetect import peakdet


def main():
    targetDirectory = getDirectory()

def getParameters(file):
    [freq, S, Y, startTemp, endTemp] = getTDMSData(file, 1, 0)
    R = sqrt(X ** 2 + Y ** 2)

    fig = plt.figure()
    plt.plot(freq, R, picker = 5)

    def onpick(event):
        global userPosList
        global userWidthList
        global userAmpList
        thisLine = event.artist
        xData = thisLine.get_xdata()
        yData = thisLine.get_ydata()
        ind = event.ind
        plt.plot(xData[ind][0], yData[ind][0], 'x', color = 'r')
        fig.canvas.draw()
        userPosList = np.append(userPosList, xData[ind][0])
        left, right = plot.xlim()
        down, up = plt.ylim()
        userWidthList = np.append(userWidthList, (right - left) / 2)
        userAmpList = np.append(userAmpList, (up - down) / 2)

    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()

    sortedInds = userPosList.argsort()
    orderedPos = userPosList[sortedInds]
    orderedWidth = userWidthList[sortedInds]
    orderedAmp = userAmpList[sortedInds]

    lorentzList = np.array([])
    for i in range(0, len(userPosListOrdered)):
        f = orderedPos[i]
        w = orderedWidth[i]
        a = orderedAmp[i]
        l = lorentz(f, w, a, -a)
        lorentzList = np.append(lorentzList, l)

    # WRITE EQUIVALENT OF CLUSTERED FITS AND NEW PARAMETER LIST

def clusteredFits(freq, R, lorentzList):
    for i in range(0, len(lorentzList)):
        l = lorentzList[i]
        if i > 0:
            lLeft = lorentzList[i - 1]
            l.leftSpace = l.frequency - lLeft.frequency
        if i < len(lorentzList) - 1:
            lRight = lorentzList[i + 1]
            l.rightSpace = lRight.frequency - l.frequency

    for i in range (0, len(lorentzList)):
        l = lorentzList[i]
        if i > 0:
            lLeft = lorentzList[i - 1]
            if l.width * 10 < l.leftSpace:
                l.batch = lLeft.batch
            else:
                l.batch = lLeft.batch + 1




def getDirectory():
    prefix = "/home/gpe/Documents/Peak-Tracker/trial-data"
    directories = [prefix + "/2_cooldown/"]
    return directories

def getFiles(directories):
    for directory in directories:
        filepaths = filepaths + sorted(glob.glob(driectory + "*.tdms"))
    return filepaths

def getTDMSData(filepath, cleanbool, plottype): # Gets desired values from each TDMS file. Heavily borrowed from original peak tracker.
    # plottype: 0 = peakplot; 1 = colorplot; 2 = tempplot

    # Get just name of file, without directory or extension.
    filename,ext = os.path.splitext(os.path.basename(filepath))
    date,time,starttemp,endtemp = filename.split("_")
    #date,time,starttemp = filename.split("_") (old filename format)
    starttemp = float(starttemp[:-1])
    endtemp = float(endtemp[:-1])

    tdms_file = TdmsFile(filepath)
    fchannel = tdms_file.object('Untitled','freq (Hz)')
    Xchannel = tdms_file.object('Untitled','X1 (V)')
    Ychannel = tdms_file.object('Untitled','Y1 (V)')
    cryochannel = tdms_file.object('Untitled','Cryostat temp (K)')
    #probechannel = tdms_file.object('Untitled','Probe temp (K)')
    freq = fchannel.data
    X = Xchannel.data
    Y = Ychannel.data
    cryotemp = cryochannel.data
    #probetemp = probechannel.data

    starttemp = cryotemp[0]
    endtemp = cryotemp[-1]

    if cleanbool == 1: #remove all columns that include NaNs
        fullsignal = np.stack((freq,X,Y)) #create an array with rows freq, X, and Y
        cleansignal = fullsignal[:,~np.isnan(fullsignal).any(axis=0)] #remove any columns that include at least one NaN

        freq = cleansignal[0]
        X = cleansignal[1]
        Y = cleansignal[2]

    else: #interpolate across all NaNs
        X = interpolatenans(X)
        Y = interpolatenans(Y)
        freq = interpolatenans(freq)

    R = sqrt(X**2 + Y**2)
    starttempvec = starttemp*np.ones(len(R))
    if plottype == 0: #peakplot
        return [freq,X,Y,starttemp,endtemp]
    elif plottype == 1: #colorplot
        return [freq/1000,starttempvec,R]
    elif plottype == 2: #tempplot
        return cryotemp

class lorentz:
    def __init__(frequency, width, amplitude, skewness):
        frequency = frequency
        width = width
        amplitude = amplitude
        skewness = skewness
        leftSpace = math.inf
        rightSpace = math.inf
        batch = 0
