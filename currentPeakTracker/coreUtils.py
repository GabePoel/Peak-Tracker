#!/usr/bin/env python

from __future__ import division
from scipy.stats import mode
from scipy.misc import derivative
import cv2
import glob
import os
import math
import sys
import numpy as np
import config as cf
import peakDetection as pd


def makeFileMap(directory):
    filePaths = sorted(glob.glob(directory + "*.tdms"))
    return filePaths


def getExportDirectory():
    root = os.getcwd()
    expDir = os.path.join(root, "exportData")
    if cf.exportDirectory is not "default":
        expDir = cf.exportDirectory
    exportFolders = os.listdir(expDir)
    existingExportNums = []
    for folder in exportFolders:
        existingExportNums += [int(folder[6:])]
    thisNum = max(existingExportNums) + 1
    newExportDirectory = os.path.join(expDir, "export" + str(thisNum))
    os.makedirs(newExportDirectory)
    if cf.exportConfig:
        exportConfig(newExportDirectory)
    return newExportDirectory


def exportConfig(location):
    root = os.getcwd()
    writeLocation = os.path.join(location, 'configExport.txt')
    writeFile = open(writeLocation, mode='w')
    configLocation = os.path.join(root, "config.py")
    configFile = open(configLocation, mode='r')
    configContents = configFile.read()
    writeFile.write(configContents)
    configFile.close()
    writeFile.close()


def exportVideo(location):
    videoExport = os.path.join(location, 'videoExport.avi')
    images = [img for img in os.listdir(location) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(location, images[0]))
    height, width, layers = frame.shape
    video = cv2.VideoWriter(videoExport, 0, 1, (width, height))
    for image in images:
        frame = cv2.imread(os.path.join(location, image))
        video.write(frame)
    video.release()
    cv2.destroyAllWindows()


def paramSort(p):
    newAmpList = p[0::4]
    newSkewList = p[1::4]
    newPosList = p[2::4]
    newWidthList = p[3::4]
    newSortedInds = newPosList.argsort()
    sortedNewAmpList = newAmpList[newSortedInds]
    sortedNewSkewList = newSkewList[newSortedInds]
    sortedNewPosList = newPosList[newSortedInds]
    sortedNewWidthList = newWidthList[newSortedInds]
    updatedParamSet = []
    for i in range(0, len(newPosList)):
        updatedParamSet.append(sortedNewAmpList[i])
        updatedParamSet.append(sortedNewSkewList[i])
        updatedParamSet.append(sortedNewPosList[i])
        updatedParamSet.append(sortedNewWidthList[i])
    return updatedParamSet


def widthExpander(paramSet, freq, R, growFactor=1, grown=False,
                  baseFactor=None):
    if baseFactor is None:
        baseFactor = cf.widthExpansionBase
    freqMin = paramSet[2] - \
        cf.widthExpansionForced * growFactor * baseFactor * paramSet[3]
    freqMax = paramSet[-2] + \
        cf.widthExpansionForced * growFactor * baseFactor * paramSet[-1]
    freqMin = min(freqMax, freqMin)
    freqMax = max(freqMax, freqMin)
    freqSubset = freq[(freq < freqMax) & (freq > freqMin)]
    if freqSubset.size == 1:
        return widthExpander(paramSet, freq, R, growFactor + 1, True)
    else:
        RSubset = R[(freq < freqMax) & (freq > freqMin)]
        return freqSubset, RSubset, grown


def updateProgress(currentValue, finalValue):
    inProgress = str(100 * (currentValue / finalValue))
    progress = truncateDecimalString(inProgress)
    displayProgress(progress)


def displayProgress(progress):
    sys.stdout.write("  " + progress + "% complete")
    sys.stdout.write("\r")


def bugMe(alert):
    alertSpace = 20 - len(alert)
    bA = "~" * 40
    leftSpace = int(math.floor(alertSpace / 2))
    rightSpace = int(math.ceil(alertSpace / 2))
    pL = "~" * leftSpace
    pR = "~" * rightSpace
    toPrint = bA + pL + "| " + alert + " |" + pR + bA
    print(" ")
    print(" ")
    print(toPrint)


def checkFrequency(newFreq, minFreq, maxFreq):
    if newFreq > maxFreq or newFreq < minFreq:
        return True
    else:
        return False


def checkParams(newParams, oldParams, minFreq, maxFreq):
    newAmps = newParams[0::4]
    newSkew = newParams[1::4]
    newFreq = newParams[2::4]
    newWids = newParams[3::4]
    oldAmps = oldParams[0::4]
    oldSkew = oldParams[1::4]
    oldFreq = oldParams[2::4]
    oldWids = oldParams[3::4]
    retAmps = np.array([])
    retSkew = np.array([])
    retFreq = np.array([])
    retWids = np.array([])
    retParams = np.array([])
    exp = cf.widthExpansionLimit
    con = cf.widthContractionLimit
    holdBool = False
    for i in range(0, len(newAmps)):
        testWids = ((newWids[i] / oldWids[i]) > exp) or \
                   ((oldWids[i] / newWids[i]) > con)
        testAmps = newAmps[i] < 0.000003
        testFreq = checkFrequency(newFreq[i], minFreq, maxFreq)
        if testAmps or testWids or testFreq:
            retAmps = np.append(retAmps, oldAmps[i])
            retSkew = np.append(retSkew, oldSkew[i])
            retFreq = np.append(retFreq, oldFreq[i])
            retWids = np.append(retWids, oldWids[i])
            holdBool = True
        else:
            retAmps = np.append(retAmps, newAmps[i])
            retSkew = np.append(retSkew, newSkew[i])
            retFreq = np.append(retFreq, newFreq[i])
            retWids = np.append(retWids, newWids[i])
            holdBool = False or holdBool
        retParams = np.append(retParams, retAmps[i])
        retParams = np.append(retParams, retSkew[i])
        retParams = np.append(retParams, retFreq[i])
        retParams = np.append(retParams, retWids[i])
    return retParams, holdBool


def findNearest(array, valueArray):
    toReturn = np.array([])
    array = np.asarray(array)
    for v in valueArray:
        idx = (np.abs(array - v)).argmin()
        toReturn = np.append(toReturn, idx)
    return toReturn.astype(int)


def truncateDecimalString(decimalString):
    parts = decimalString.split('.')
    stringPiece = parts[0] + '.'
    stringPiece += parts[1][:2]
    return stringPiece


def demoPlot():
    thisDirectory = os.getcwd() + '/sampleData/trialData/2_cooldown'
    return thisDirectory


def roughAmplitude(RSubset, oldAmplitude):
    noiseEst = np.std(RSubset)
    if oldAmplitude < cf.amplitudeNoiseTolerance * noiseEst:
        return abs(max(RSubset) - min(RSubset))
    else:
        return oldAmplitude


def prepPeaks(skeleton, givenPeaks=None):
    if givenPeaks is None:
        detection = pd.ManualPeakSelection(skeleton)
    else:
        detection = pd.GivenPeakSelection(givenPeaks)
    return detection


def trimZeros(array):
    return np.trim_zeros(array)

def numericalDerivative(X, Y):
    return
