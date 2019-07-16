#!/usr/bin/env python

from __future__ import division

import glob
import os

import numpy as np

from nptdms import TdmsFile


# The primary data structure that holds all the data for a given TDMS file
class FileData:
    def __init__(self, freq, X, Y, startTemp, endTemp, colorFreq, startTempVec,
                 R, cryoTemp, filePath):
        self.freq = freq
        self.X = X
        self.Y = Y
        self.startTemp = startTemp
        self.endTemp = endTemp
        self.colorFreq = colorFreq
        self.startTempVec = startTempVec
        self.R = R
        self.cryoTemp = cryoTemp

    def peakPlotParams(self):
        return [self.freq, self.X, self.Y, self.startTemp, self.endTemp]

    def colorPlotParams(self):
        return [self.freq, self.colorFreq, self.startTempVec, self.R]

    def tempPlotParams(self):
        return self.cryoTemp

    def filePath(self):
        return self.filePath


# Gives useful parameters from the given file
def getData(filePath, cleanBool=True):
    # plotTypes: "peakPlot", "colorPlot", "tempPlot"

    # Get file name without directory or extension
    fileName, ext = os.path.splitext(os.path.basename(filePath))
    date, time, startTemp, endTemp = fileName.split("_")
    startTemp = float(startTemp[:-1])
    endTemp = float(endTemp[:-1])

    tdmsFile = TdmsFile(filePath)
    fChannel = tdmsFile.object('Untitled', 'freq (Hz)')
    xChannel = tdmsFile.object('Untitled', 'X1 (V)')
    yChannel = tdmsFile.object('Untitled', 'Y1 (V)')
    cryoChannel = tdmsFile.object('Untitled', 'Cryostat temp (K)')

    freq = fChannel.data
    X = xChannel.data
    Y = yChannel.data
    cryoTemp = cryoChannel.data

    startTemp = cryoTemp[0]
    endTemp = cryoTemp[-1]

    if cleanBool == True:
        # create an array with rows freq, X, and Y
        fullSignal = np.stack((freq, X, Y))
        # remove any columns that include at least one NaN
        cleanSignal = fullSignal[:, ~np.isnan(fullSignal).any(axis=0)]

        freq = cleanSignal[0]
        X = cleanSignal[1]
        Y = cleanSignal[2]

    else:  # interpolate across all NaNs
        X = interpolateNans(X)
        Y = interpolateNans(Y)
        freq = interpolateNans(freq)

    R = np.sqrt(X ** 2 + Y ** 2)
    startTempVec = startTemp * np.ones(len(R))
    colorFreq = freq / 1000

    return FileData(freq, X, Y, startTemp, endTemp, colorFreq, startTempVec, R,
                    cryoTemp, filePath)


# Looks at the data in the given file and finds its min and max frequencies
def getDataCriteria(data, dataMaxFreq = np.inf, dataMinFreq = -np.inf):
    if dataMinFreq < min(data.freq):
        dataMinFreq = min(data.freq)
    if dataMaxFreq > max(data.freq):
        dataMaxFreq = max(data.freq)

    return dataMinFreq, dataMaxFreq


def interpolateNans(inputArray):
    if np.isnan(inputArray).any():
        # if array contains any NaNs, interpolate over them
        boolArray = ~np.isnan(inputArray)
        goodIndices = boolArray.nonzero()[0]
        goodPoints = inputArray[~np.isnan(inputArray)]
        badIndices = np.isnan(inputArray).nonzero()[0]
        inputArray[np.isnan(inputArray)] = np.interp(badIndices, goodIndices,
                                                     goodPoints)
    return inputArray
