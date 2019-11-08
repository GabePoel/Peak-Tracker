import warnings
import numpy as np
import modularPeakFit as pk
import modularConfig as conf
from scipy.optimize import least_squares
from scipy.optimize import curve_fit

def safeLeastSquares(fit, parameters, args=None):
    ftol = conf.terminationCostTolerance
    gtol = conf.terminationGradientTolerance
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
        # print("~~ new lorentz data ~~")
        xMin = min(dataBatch.getLorentz(lorentzList[i][0]).xData)
        xMax = max(dataBatch.getLorentz(lorentzList[i][len(lorentzList[i]) \
            - 1]).xData)
        minMax = (xMin, xMax)
        xData = dataBatch.getData(minMax, "point", "freq", "freq")
        yData = dataBatch.getData(minMax, "point", "r", "freq")
        backgroundParameters = getLocalBackgroundParameters(xData, yData)
        fitParameters = np.append(parameterList[i], backgroundParameters)
        # print("fitParameters: " + str(fitParameters[:-2]))
        fitInputWeights = np.ones(len(xData))
        fitResults = safeLeastSquares(pk.multiLorentzResidualFit, fitParameters, \
            args=(xData, yData, fitInputWeights))
        # print("fitResults:    " + str(fitResults.x[:-2]))
        # print("changes:       " + str(fitParameters[:-2] - fitResults.x[:-2]))
        yFitData = pk.multiLorentzFit(fitResults.x, xData)
        fitList.append((xData, yFitData))
        for j in lorentzList[i]:
            dataBatch.lorentzArray[j].fitCost = fitResults.cost
    # print("index: " + str(dataBatch.index))
    return fitList

def getMultiFitParameterList(dataBatch, includeBackground=False):
    parameterList = dataBatch.getMultiParameters()
    lorentzList = dataBatch.groupLorentz()
    outputParameterArray = np.array([])
    for i in range(0, len(parameterList)):
        # print("~~ new lorentz fit~~")
        xMin = min(dataBatch.getLorentz(lorentzList[i][0]).xData)
        xMax = max(dataBatch.getLorentz(lorentzList[i][len(lorentzList[i]) \
            - 1]).xData)
        minMax = (xMin, xMax)
        # print("minMax: " + str(minMax))
        xData = dataBatch.getData(minMax, "point", "freq", "freq")
        yData = dataBatch.getData(minMax, "point", "r", "freq")
        backgroundParameters = getLocalBackgroundParameters(xData, yData)
        fitParameters = np.append(parameterList[i], backgroundParameters)
        # print("fitParameters: " + str(fitParameters[:-2]))
        fitInputWeights = np.ones(len(xData))
        fitResults = safeLeastSquares(pk.multiLorentzResidualFit, fitParameters, \
            args=(xData, yData, fitInputWeights))
        # print("fitResults:    " + str(fitResults.x[:-2]))
        # print("changes:       " + str(fitParameters[:-2] - fitResults.x[:-2]))
        if not includeBackground:
            fitResults = fitResults.x[:-2]
        # print("fit results: " + str(fitResults))
        outputParameterArray = np.append(outputParameterArray, fitResults)
    outputParameterList = np.split(outputParameterArray, len(outputParameterArray) / 4)
    # print("change: " + str(outputParameterList[1][3]))
    # print("output parameter list: " + str(outputParameterList))
    # print("index: " + str(dataBatch.index))
    return outputParameterList
    