import warnings
import numpy as np
import modularPeakFit as pk
import modularConfig as conf
from scipy.optimize import least_squares
from scipy.optimize import curve_fit

def safeLeastSquares(fit, parameters, args=None):
    ftol = conf.terminationCostTolerance
    gtol = conf.terminationCostTolerance
    xtol = conf.terminationIndependentTolerance
    warnings.simplefilter(action='ignore', category=FutureWarning)
    return least_squares(fit, parameters, ftol=ftol, gtol=gtol, xtol=xtol, \
        args=args, method=conf.leastSquaresMethod)

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

def getFitData(singleLorentz, xData):
    fitParameters = singleLorentz.getSingleParameters()
    xData = singleLorentz.xData
    yData = singleLorentz.yData
    backgroundParameters = getLocalBackgroundParameters(xData, yData)
    fitParameters = np.append(fitParameters, backgroundParameters)
    fitInputWeights = np.ones(len(xData))
    fitResults = least_squares(pk.multiLorentzResidualFit, fitParameters,  \
        ftol=1e-10, args=(xData, yData, fitInputWeights), \
            method=conf.leastSquaresMethod)
    yFitData = pk.multiLorentzFit(fitResults.x, xData)
    return yFitData

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
        fitResults = safeLeastSquares(pk.multiLorentzResidualFit, fitParameters, \
            args=(xData, yData, fitInputWeights))
        yFitData = pk.multiLorentzFit(fitResults.x, xData)
        fitList.append((xData, yFitData))
        for j in lorentzList[i]:
            dataBatch.lorentzArray[j].fitCost = fitResults.cost
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
        fitResults = safeLeastSquares(pk.multiLorentzResidualFit, fitParameters, \
            args=(xData, yData, fitInputWeights))
        if not includeBackground:
            fitResults = fitResults.x[:-2]
        outputParameterArray = np.append(outputParameterArray, fitResults)
    outputParameterList = np.split(outputParameterArray, len(outputParameterArray) / 4)
    return outputParameterList
    