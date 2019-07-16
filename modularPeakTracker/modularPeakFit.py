import numpy as np

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


def anharmonic(p, x):
    print("now calling anharmonic")
    return p[0] - p[1] / (np.exp(p[2] / x) - 1)


def anharmonicresidual(p, x, z, weights):
    print("now calling anharmonicresidual")
    return (anharmonic(p, x) - z) * weights


def interpolatenans(inputarray):
    print("now calling interpolatenans")
    if np.isnan(inputarray).any():
        # if array contains any NaNs, interpolate over them
        boolarray = ~np.isnan(inputarray)
        goodindices = boolarray.nonzero()[0]
        goodpoints = inputarray[~np.isnan(inputarray)]
        badindices = np.isnan(inputarray).nonzero()[0]
        inputarray[np.isnan(inputarray)] = np.interp(badindices, goodindices,
                                                     goodpoints)
    return inputarray
