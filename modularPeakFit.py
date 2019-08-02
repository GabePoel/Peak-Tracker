import numpy as np

# lorentzian (only peak; not absorptive)
def lorentzFit(p, x):
    return p[0] / np.sqrt((p[1] ** 2 - x ** 2) ** 2 + p[2] ** 2 * x ** 2)


def lorentzResidualFit(p, x, z):
    return lorentzFit(p, x) - z


def lorentzWithBackgroundFit(p, x):
    return p[0] / np.sqrt((p[1] ** 2 - x ** 2) ** 2 + p[2] ** 2 * x ** 2) + p[3]


def lorentzWithBackgroundResidualFit(p, x, z):
    return lorentzWithBackgroundFit(p, x) - z

# p: fit parameters; x: frequencies; z: data


def singleLorentzFit(p, x):
    return (p[0] + p[1] * (x - p[2])) / (((x - p[2]) ** 2) + 1 / 4 * (p[3] ** 2))
    # using Lorentzian form from Zadler's paper


def singleLorentzResidualFit(p, x, z):
    return singleLorentzFit(p, x) - z


def multiLorentzFit(p, x):
    m = p[-1]
    b = p[-2]
    lorentzCount = int((len(p) - 2) / 4)
    result = m * x + np.ones(len(x)) * b
    for i in range(0, lorentzCount):
        parameters = p[i * 4:i * 4 + 4]
        # amplitude, skewness, position, FWHM
        # penalize positions outside freq range, as well as negative FWHM
        result = result + singleLorentzFit(parameters, x)
        if parameters[2] < x[0]:
            result = result + x * 1000000
        if parameters[2] > x[-1]:
            result = result + x * 1000000
        if parameters[3] < 0:
            result = result + x * 1000000
    return result


def multiLorentzResidualFit(p, x, z, weights):
    return (multiLorentzFit(p, x) - z) * weights


def singleLorentzWithBackgroundFit(p, x):
    return (p[0] + p[1] * (x - p[2])) / ((x - p[2]) ** 2 + 1 / 4 * p[3] ** 2) \
        + p[4] + x * p[5]


def singleLorentzWithBackgroundResidualFit(p, x, z):
    return singleLorentzWithBackgroundFit(p, x) - z


def anharmonicFit(p, x):
    return p[0] - p[1] / (np.exp(p[2] / x) - 1)


def anharmonicResidualFit(p, x, z, weights):
    return (anharmonicFit(p, x) - z) * weights


def interpolateNaNs(inputArray):
    if np.isnan(inputArray).any():
        # if array contains any NaNs, interpolate over them
        boolArray = ~np.isnan(inputArray)
        goodIndices = boolArray.nonzero()[0]
        goodPoints = inputArray[~np.isnan(inputArray)]
        badIndices = np.isnan(inputArray).nonzero()[0]
        inputArray[np.isnan(inputArray)] = np.interp(badIndices, goodIndices, \
            goodPoints)
    return inputArray
