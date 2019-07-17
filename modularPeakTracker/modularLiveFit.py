import warnings
import numpy as np
import modularPeakFit as pk
from scipy.optimize import least_squares

def getPostLorentz(preLorentz, includeBackground=False):
    freq = preLorentz.peakFrequency
    amp = preLorentz.amplitude
    skew = preLorentz.skew
    width = preLorentz.fullWidthHalfMaximum
    xData = preLorentz.xData
    yData = preLorentz.yData
    guessParameters = np.array([amp, skew, freq, width])
    fitInputWeights = np.ones(len(xData))
    if len(guessParameters) == 4:
        guessParameters = np.append(guessParameters, \
            getLocalBackgroundParameters(xData, yData))
    fitResult = least_squares(pk.multilorentzresidual, guessParameters,  \
         ftol=1e-10, args=(xData, yData, fitInputWeights))
    returnParameters = fitResult.x
    if includeBackground:
        return returnParameters
    return returnParameters[:-2]

def getFitData(singleLorentz, xData):
    fitParameters = singleLorentz.getSingleParameters()
    xData = singleLorentz.xData
    yData = singleLorentz.yData
    backgroundParameters = getLocalBackgroundParameters(xData, yData)
    fitParameters = np.append(fitParameters, backgroundParameters)
    fitInputWeights = np.ones(len(xData))
    fitResults = least_squares(pk.multilorentzresidual, fitParameters,  \
         ftol=1e-10, args=(xData, yData, fitInputWeights))
    yFitData = pk.multilorentz(fitResults.x, xData)
    return yFitData

def getLocalBackgroundParameters(xData, yData):
    defaultOffset = np.mean(yData[0] + yData[len(yData) - 1])
    slope, offset = 0, defaultOffset
    with warnings.catch_warnings():
        warnings.filterwarnings('error')
        try:
            [slope, offset] = np.polyfit(xData, yData, deg=1)
        except np.RankWarning:
            print("Background fit issue. Using default background.")
    return np.array([slope, offset])

def reduceData(parameters, xData):
    xMax = parameters[2] + 2 * parameters[3]
    xMin = parameters[2] - 2 * parameters[3]

def getMultiFitData(dataBatch):
    parameterList = dataBatch.getMultiParameters()
    lorentzList = dataBatch.groupLorentz()
    fitList = []
    for i in range(0, len(parameterList)):
        xMin = min(dataBatch.getLorentz(lorentzList[i][0]).xData)
        xMax = max(dataBatch.getLorentz(lorentzList[i][len(lorentzList[i]) \
            - 1]).xData)
        minMax = (xMin, xMax)
        xData = dataBatch.getData(minMax, "point", "freq", "freq")
        yData = dataBatch.getData(minMax, "point", "r", "freq")
        backgroundParameters = getLocalBackgroundParameters(xData, yData)
        fitParameters = np.append(parameterList[i], backgroundParameters)
        fitInputWeights = np.ones(len(xData))
        fitResults = least_squares(pk.multilorentzresidual, fitParameters, \
            ftol=1e-19, args=(xData, yData, fitInputWeights))
        yFitData = pk.multilorentz(fitResults.x, xData)
        fitList.append((xData, yFitData))
    return fitList

def getMultiFitParameterList(dataBatch, includeBackground=False):
    parameterList = dataBatch.getMultiParameters()
    lorentzList = dataBatch.groupLorentz()
    outputParameterArray = np.array([])
    for i in range(0, len(parameterList)):
        xMin = min(dataBatch.getLorentz(lorentzList[i][0]).xData)
        xMax = max(dataBatch.getLorentz(lorentzList[i][len(lorentzList[i]) \
            - 1]).xData)
        minMax = (xMin, xMax)
        xData = dataBatch.getData(minMax, "point", "freq", "freq")
        yData = dataBatch.getData(minMax, "point", "r", "freq")
        backgroundParameters = getLocalBackgroundParameters(xData, yData)
        fitParameters = np.append(parameterList[i], backgroundParameters)
        fitInputWeights = np.ones(len(xData))
        fitResults = least_squares(pk.multilorentzresidual, fitParameters, \
            ftol=1e-19, args=(xData, yData, fitInputWeights))
        if not includeBackground:
            fitResults = fitResults.x[:-2]
        outputParameterArray = np.append(outputParameterArray, fitResults)
    outputParameterList = np.split(outputParameterArray, len(outputParameterArray) / 4)
    return outputParameterList
    