import warnings
import numpy as np
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
    fitResult = least_squares(multilorentzresidual, guessParameters,  \
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
    fitResults = least_squares(multilorentzresidual, fitParameters,  \
         ftol=1e-10, args=(xData, yData, fitInputWeights))
    yFitData = multilorentz(fitResults.x, xData)
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
        fitResults = least_squares(multilorentzresidual, fitParameters, \
            ftol=1e-19, args=(xData, yData, fitInputWeights))
        yFitData = multilorentz(fitResults.x, xData)
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
        fitResults = least_squares(multilorentzresidual, fitParameters, \
            ftol=1e-19, args=(xData, yData, fitInputWeights))
        if not includeBackground:
            fitResults = fitResults.x[:-2]
        outputParameterArray = np.append(outputParameterArray, fitResults)
    outputParameterList = np.split(outputParameterArray, len(outputParameterArray) / 4)
    print("outputParamterList:")
    print(outputParameterList)
    return outputParameterList

# lorentzian (only peak; not absorptive)
def lorentz(p, x):
    # print("now calling lorentz")
    return p[0] / np.sqrt((p[1] ** 2 - x ** 2) ** 2 + p[2] ** 2 * x ** 2)


def lorentzresidual(p, x, z):
    # print("now calling lorentzresidual")
    return lorentz(p, x) - z


def lorentzwithbg(p, x):
    # print("now calling lorentzwithbg")
    return p[0] / np.sqrt((p[1] ** 2 - x ** 2) ** 2 + p[2] ** 2 * x ** 2) + p[3]


def lorentzwithbgresidual(p, x, z):
    # print("now calling lorentzwithbgresidual")
    return lorentzwithbg(p, x) - z

# p: fit parameters; x: frequencies; z: data


def singlelorentz(p, x):
    # print("now calling singlelorentz")
    return (p[0] + p[1] * (x - p[2])) / ((x - p[2]) ** 2 + 1 / 4 * p[3] ** 2)
    # using Lorentzian form from Zadler's paper


def singlelorentzresidual(p, x, z):
    # print("now calling singlelorentzresidual")
    return singlelorentz(p, x) - z


def multilorentz(p, x):
    # print("now calling multilorentz")
    m = p[-1]
    b = p[-2]
    numlorentz = int((len(p) - 2) / 4)
    result = m * x + np.ones(len(x)) * b
    for i in range(0, numlorentz):
        params = p[i * 4:i * 4 + 4]
        # amplitude, skewness, position, FWHM
        # penalize positions outside freq range, as well as negative FWHM
        result = result + singlelorentz(params, x)
        if params[2] < x[0]:
            result = result + x * 1000000
        if params[2] > x[-1]:
            result = result + x * 1000000
        if params[3] < 0:
            result = result + x * 1000000
    return result


def multilorentzresidual(p, x, z, weights):
    # print("now calling multilorentzresidual")
    return (multilorentz(p, x) - z) * weights


def singlelorentzwithbg(p, x):
    # print("now calling singlelorentzwithbg")
    return (p[0] + p[1] * (x - p[2])) / ((x - p[2]) ** 2 + 1 / 4 * p[3] ** 2) \
        + p[4] + x * p[5]


def singlelorentzwithbgresidual(p, x, z):
    # print("now calling singlelorentzwithbgresidual")
    return singlelorentzwithbg(p, x) - z
