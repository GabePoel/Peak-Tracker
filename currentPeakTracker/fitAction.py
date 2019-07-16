#!/usr/bin/env python

from __future__ import division
from scipy.optimize import least_squares
import os
import sys
import warnings
import time
import copy
import matplotlib.pyplot as plt
import numpy as np
import config as cf
import coreUtils as cu
import dataManagement as dm
import fitParams as fp


class FitProcedure:

    def __init__(self, totalMinFreq, totalMaxFreq, initialParams, save, count):
        self.totalMinFreq = totalMinFreq
        self.totalMaxFreq = totalMaxFreq
        self.initialParams = initialParams
        self.userPosList = np.array([])
        self.userWidthList = np.array([])
        self.userAmpList = np.array([])
        self.totalPeakList = []
        self.totalTempList = []
        self.skeleton = save
        self.count = count
        self.ax = save.ax
        self.fig = save.fig
        self.window = save.window
        self.tempBG = np.zeros(1)

    def clusteredFits(self, freq, R, fullParamList):
        userPosList, userWidthList, splitParams, newParamList, ptsBool, \
            fitPlot, fitBool, fitRange = self.setupClusteredFits(freq, R,
                                                                 fullParamList)
        flatPlot = []
        for oldParams in splitParams:
            oldParams = cu.paramSort(oldParams)
            fitResult, grownBool, flatResult = \
                self.generatePeakPlotFit(freq, R, oldParams)
            fitOutputParams = fitResult.x
            flatOutputParams = flatResult.x
            newParams = fitOutputParams[:-2]
            oldParams = np.asarray(oldParams)
            newParams, flatLineBool = cu.checkParams(newParams, oldParams,
                                                     self.totalMinFreq,
                                                     self.totalMaxFreq)
            newParamList = np.append(newParamList, newParams)
            newParamList = cu.paramSort(newParamList)
            displayBool = not (flatLineBool or grownBool)
            predictedPeaks = newParams[2::4]
            predictedWidths = newParams[3::4]
            if cf.widthCorrectionEnable:
                predictedWidths = predictedWidths * cf.widthCorrectionFactor
            disp = cf.compactDisplayLevel
            plotStart = min(predictedPeaks) - (disp * max(predictedWidths))
            plotEnd = max(predictedPeaks) + (disp * max(predictedWidths))
            freqPart = freq[(freq < plotEnd) & (freq > plotStart)]
            fitRange += [freqPart]
            fitPlot += [fp.multilorentz(fitOutputParams, freqPart)]
            flatPlot += [fp.multilorentz(flatOutputParams, freqPart)]
            fitBool += [displayBool]
            ptsBool = self.pointDisplayConfirmation(ptsBool, displayBool,
                                                    len(predictedPeaks))
        predictedPeaks = newParamList[2::4]
        predictedWidths = newParamList[3::4]
        plotStart = min(predictedPeaks) - (3 * max(predictedWidths))
        plotEnd = max(predictedPeaks) + (3 * max(predictedWidths))
        plotRange = freq[(freq < plotEnd) & (freq > plotStart)]
        return newParamList, fitPlot, fitRange, fitBool, flatPlot, plotRange, \
            ptsBool

    def filterBackground(self, freq, R, fitRange, flatPlot):
        # print("A1: " + str(max(self.tempBG)))
        for i in range(0, len(fitRange)):
            # print("B1: " + str(max(R)))
            RSubtractionRange = cu.findNearest(freq, fitRange[i])
            minIdx = min(RSubtractionRange) - 1
            maxIdx = max(RSubtractionRange) + 1
            numSteps = len(RSubtractionRange)
            minR = R[minIdx]
            maxR = R[maxIdx]
            RDist = maxR - minR
            filler = np.arange(minR, maxR, RDist / numSteps)
            if filler.shape != R[RSubtractionRange].shape:
                filler = np.resize(filler, R[RSubtractionRange].shape)
            # print("C1: " + str(max(filler)))
            # print("D1: " + str(max(flatPlot[i])))
            # print("D2: " + str(min(flatPlot[i])))
            # print("B2: " + str(max(R)))
            R[RSubtractionRange] = R[RSubtractionRange] - flatPlot[i] + filler
            # print("B3: " + str(max(R)))
        BG = np.poly1d(np.polyfit(freq, R, deg=cf.backgroundSuppressionDegree))
        # print("A2: " + str(max(self.tempBG)))
        R = R - BG(freq)
        return BG(freq)

    def trackPeaks(self, initParamList, filePaths):
        numLorentz, peakPositions, peakWidths, toDisplay, startTemps = \
            self.setupPeakPlot(initParamList, filePaths)
        for i in range(0, len(filePaths)):
            cu.updateProgress(i, self.count)
            data = dm.getData(filePaths[i])
            [freq, X, Y, startTemp, endTemp] = data.peakPlotParams()
            # print("M1: " + str(max(self.tempBG)))
            R = copy.copy(data.R)
            # if W.shape != self.tempBG.shape:
            #     self.tempBG = np.resize(self.tempBG, W.shape)
            # print("M2: " + str(max(self.tempBG)))
            # R = copy.copy(W) - self.tempBG
            # print("M3: " + str(max(self.tempBG)))
            newParamList, fitPlot, fitRange, fitBool, flatPlot, plotRange, \
                ptsBool = self.clusteredFits(freq, R, initParamList)
            peakPositions[:, i] = newParamList[2::4]
            peakWidths[:, i] = newParamList[3::4]
            toDisplay[:, i] = ptsBool
            startTemps[i] = startTemp
            initParamList = newParamList
            plotRange = cu.findNearest(freq, plotRange).astype(int)
            predictedPeaks = cu.findNearest(freq,
                                            newParamList[2::4]).astype(int)
            # print("M3.5: " + str(max(self.tempBG)))
            if cf.backgroundSuppression:
                self.tempBG = self.filterBackground(freq, R, fitRange, flatPlot)
            # print("M4: " + str(max(self.tempBG)))
            self.displayPeakPlot(freq, R, predictedPeaks, \
                fitRange, fitPlot, fitBool, flatPlot, plotRange)
            # print("M5: " + str(max(self.tempBG)))
        cu.displayProgress("100")
        plt.clf()
        merge = peakPositions
        if not cf.displayLostData:
            merge = np.multiply(peakPositions, toDisplay)
        for i in range(0, numLorentz):
            if cf.displayLostData:
                xFilter = startTemps
            else:
                xFilter = cu.trimZeros(np.multiply(startTemps,
                                                   toDisplay[i, :]))
            yFilter = cu.trimZeros(merge[i, :])
            plt.plot(xFilter, yFilter)
        self.window.quickUpdate()
        if cf.exportVideo:
            self.window.saveVid()
        self.window.savePlot('resultExport', False)

    def pointDisplayConfirmation(self, confirmationArray, confirmationBool,
                                 numInputs):
        if confirmationBool:
            confirmationArray = np.append(confirmationArray,
                np.ones(numInputs))
        else:
            confirmationArray = np.append(confirmationArray,
                np.zeros(numInputs))
        return confirmationArray

    def generatePeakPlotFit(self, freq, R, oldParams):
        freqSubset, RSubset, grownBool = cu.widthExpander(oldParams, freq, R)
        defaultOffset = np.mean(RSubset)
        slope, offset = self.localBackgroundProcessing(freqSubset, \
            RSubset, defaultOffset)
        fitInputWeights = np.ones(len(freqSubset))
        if cf.amplitudeCorrectionEnabled:
            for i in range(0, len(oldParams[0::4])):
                oldParams[0::4][i] = cu.roughAmplitude(RSubset,
                                                       oldParams[0::4][i])
        fitInputParams = np.append(oldParams, [offset, slope])
        flatInputParams = np.append(oldParams, [offset, slope])
        fitResult = least_squares(fp.multilorentzresidual, fitInputParams, \
            ftol=1e-10, args=(freqSubset, RSubset, fitInputWeights))
        flatResult = least_squares(fp.multilorentzresidual, flatInputParams, \
            ftol=1e-10, args=(freqSubset, RSubset, fitInputWeights))
        return fitResult, grownBool, flatResult


    def displayPeakPlot(self, freq, R, predictedPeaks, fitRange, fitPlot,
                        fitBool, flatPlot, plotRange):
        c1 = cf.peakPlotBackgroundColor
        c2 = cf.peakPlotFitColor
        c3 = cf.peakPlotPeakColor
        plt.clf()
        if cf.displayScale is "all":
            plotRange = np.arange(len(freq))
        plt.plot(freq[predictedPeaks], R[predictedPeaks], "x", color=c3)
        plt.plot(freq[plotRange], R[plotRange], color=c1)
        for i in range(0, len(fitRange)):
            if fitBool[i] or cf.displayLostData:
                plt.plot(fitRange[i], fitPlot[i], color=c2)
        if cf.backgroundSuppression:
            plt.plot(freq[plotRange], self.tempBG[plotRange])
            # plt.plot(freq[plotRange], (R - self.tempBG)[plotRange])
        if cf.exportImages:
            self.window.savePlot('frameExport', True)
        if cf.liveUpdate:
            self.window.quickUpdate()
            self.window.quickPause(0.01)

    def localBackgroundProcessing(self, freqSubset, RSubset, defaultOffset):
        slope, offset = 0, defaultOffset
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                [slope, offset] = np.polyfit(freqSubset, RSubset, deg=1)
            except np.RankWarning:
                cu.bugMe("Polyfit is mad.")
                print(freqSubset.size)
        return slope, offset

    def setupPeakPlot(self, initParamList, filePaths):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Tracking progress so far:")
        print()
        numLorentz = int(len(initParamList) // 4)
        peakPositions = np.zeros((numLorentz, len(filePaths)))
        peakWidths = np.zeros((numLorentz, len(filePaths)))
        toDisplay = np.zeros((numLorentz, len(filePaths)))
        startTemps = np.zeros(len(filePaths))
        return numLorentz, peakPositions, peakWidths, toDisplay, startTemps

    def setupClusteredFits(self, freq, R, fullParamList):
        fullParamList = np.array(fullParamList)
        userPosList = fullParamList[2::4]
        userWidthList = fullParamList[3::4]
        spacesBetween = userPosList[1:] - userPosList[:-1]
        if cf.forceSingleLorentz:
            splitDist = 0
        else:
            splitDist = cf.peakSeparationFactor
        splitIndices =  \
            np.where((spacesBetween > splitDist * userWidthList[:-1]) &
                     (spacesBetween > splitDist * userWidthList[1:]))
        splitParams = np.split(fullParamList, 4 * (splitIndices[0] + 1))
        newParamList = np.array([], dtype=np.integer)
        ptsBool = np.array([])
        fitRange = []
        fitPlot = []
        fitBool = []
        return userPosList, userWidthList, splitParams, newParamList, ptsBool, \
            fitPlot, fitBool, fitRange
