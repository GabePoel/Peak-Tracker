# /usr/bin/python -tt

from __future__ import division  # makes division default to floats
import numpy as np
from numpy import sqrt
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy.optimize import leastsq

from peakdetect import peakdet

import glob  # for searching directory
import os
import math

totalMaxFreq = np.inf
totalMinFreq = -totalMaxFreq

userposlist = np.array([])
userwidthlist = np.array([])
useramplist = np.array([])
totalpeaklist = []
totaltemplist = []


def main():
    print("now calling main")
    # change file path as needed

    # prefix = "/home/gpe/Documents/Peak-Tracker/trial-data"
    # directories = [prefix + "/2_cooldown/"]

    prefix = os.path.expanduser('~') + "/Box/RUS data/Sylvia/"
    directories = [prefix + "CeCoIn5/AG1800 - I/2_cooldown/"]

    filepaths = []
    for directory in directories:
        filepaths = filepaths + sorted(glob.glob(directory + "*.tdms"))
    # print(filepaths)
    for filepath in filepaths:
        prepStates(filepath)
    print("totalMinFreq: " + str(totalMinFreq))
    print("totalMaxFreq: " + str(totalMaxFreq))
    initparamlist = initializearray(filepaths[0])
    trackpeaks(initparamlist, filepaths)


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


# pull desired values from each TDMS file
def returnvals(filepath, cleanbool, plottype):
    # plottype: 0 = peakplot; 1 = colorplot; 2 = tempplot

    # get just name of file, without directory or extension
    filename, ext = os.path.splitext(os.path.basename(filepath))
    date, time, starttemp, endtemp = filename.split("_")
    # date,time,starttemp = filename.split("_") (old filename format)
    starttemp = float(starttemp[:-1])
    endtemp = float(endtemp[:-1])

    tdms_file = TdmsFile(filepath)
    fchannel = tdms_file.object('Untitled', 'freq (Hz)')
    Xchannel = tdms_file.object('Untitled', 'X1 (V)')
    Ychannel = tdms_file.object('Untitled', 'Y1 (V)')
    cryochannel = tdms_file.object('Untitled', 'Cryostat temp (K)')
    # probechannel = tdms_file.object('Untitled','Probe temp (K)')
    freq = fchannel.data
    X = Xchannel.data
    Y = Ychannel.data
    cryotemp = cryochannel.data
    # probetemp = probechannel.data

    starttemp = cryotemp[0]
    endtemp = cryotemp[-1]

    if cleanbool == 1:  # remove all columns that include NaNs
        # create an array with rows freq, X, and Y
        fullsignal = np.stack((freq, X, Y))
        # remove any columns that include at least one NaN
        cleansignal = fullsignal[:, ~np.isnan(fullsignal).any(axis=0)]

        freq = cleansignal[0]
        X = cleansignal[1]
        Y = cleansignal[2]

    else:  # interpolate across all NaNs
        X = interpolatenans(X)
        Y = interpolatenans(Y)
        freq = interpolatenans(freq)

    R = sqrt(X ** 2 + Y ** 2)
    starttempvec = starttemp * np.ones(len(R))
    if plottype == 0:  # peakplot
        return [freq, X, Y, starttemp, endtemp]
    elif plottype == 1:  # colorplot
        return [freq / 1000, starttempvec, R]
    elif plottype == 2:  # tempplot
        return cryotemp


def prepStates(filepath):
    # plottype: 0 = peakplot; 1 = colorplot; 2 = tempplot

    # get just name of file, without directory or extension
    filename, ext = os.path.splitext(os.path.basename(filepath))
    date, time, starttemp, endtemp = filename.split("_")
    # date,time,starttemp = filename.split("_") (old filename format)
    starttemp = float(starttemp[:-1])
    endtemp = float(endtemp[:-1])

    tdms_file = TdmsFile(filepath)
    fchannel = tdms_file.object('Untitled', 'freq (Hz)')
    freq = fchannel.data
    global totalMinFreq
    global totalMaxFreq
    if totalMinFreq < min(freq):
        totalMinFreq = min(freq)
    if totalMaxFreq > max(freq):
        totalMaxFreq = max(freq)


# get initial list of parameters from user
def initializearray(filepath):
    print("now calling initializearray")
    [freq, X, Y, starttemp, endtemp] = returnvals(filepath, 1, 0)
    R = sqrt(X ** 2 + Y ** 2)

    fig = plt.figure()
    plt.plot(freq, R, picker=5)

    # allows user to interactively input initial parameters for each resonance.
    # when user clicks, position of click is peak position; height and width
    # of plot are used for FWHM and amplitude.
    def onpick(event):
        print("now calling onpick")
        global userposlist
        global userwidthlist
        global useramplist
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        plt.plot(xdata[ind][0], ydata[ind][0], 'x',
                 color='r')  # mark selected point
        fig.canvas.draw()
        # add position of peak to list
        userposlist = np.append(userposlist, xdata[ind][0])
        left, right = plt.xlim()
        down, up = plt.ylim()
        # add approximation of FWHM to list
        userwidthlist = np.append(userwidthlist, (right - left) / 2)
        # add approximation of amplitude to list
        useramplist = np.append(useramplist, (up - down) / 2)


    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
    print("ran plt.show() after completing onpicks")

    # sort lists so they are in increasing order based on resonance position
    sortedinds = userposlist.argsort()
    userposlist_ordered = userposlist[sortedinds]
    userwidthlist_ordered = userwidthlist[sortedinds]
    useramplist_ordered = useramplist[sortedinds]

    fullparamlist = np.array([])
    for i in range(0, len(userposlist_ordered)):
        position = userposlist_ordered[i]
        FWHM = userwidthlist_ordered[i]
        amplitude = useramplist_ordered[i]

        # amplitude, skewness, position, FWHM
        # TODO: double check skewness
        params = [amplitude, -amplitude, position, FWHM]
        fullparamlist = np.append(fullparamlist, params)

    print("fullparamlist:")
    print("    " + str(fullparamlist))
    fullparamlist = cleanBadParams(fullparamlist)
    print("new fullparamlist:")
    print(str(fullparamlist))
    # wait.sleep(5)
    newparamlist = clusteredfits(freq, R, fullparamlist)
    print("done with initializearray")
    return newparamlist


# fit each group of resonances using the multilorentz function
def clusteredfits(freq, R, fullparamlist):
    global totalMinFreq
    global totalMaxFreq
    # print("now calling clusteredfits")
    userposlist = fullparamlist[2::4]
    userwidthlist = fullparamlist[3::4]

    # split frequency spectrum into independent chunks of clustered resonances
    # spaces between resonance peaks
    spacesbetween = userposlist[1:] - userposlist[:-1]
    # print("spacesbetween:")
    # print(spacesbetween)
    # split the peaks into groups as long as there is a space of more than
    # 10*FWHM from the peaks on either side of the space
    splitindices = np.where((spacesbetween > 10 * userwidthlist[:-1]) &
                            (spacesbetween > 10 * userwidthlist[1:]))
    # print("reviewed indices:")
    # print(userwidthlist)
    # print(userwidthlist[:-1])
    # print(userwidthlist[1:])
    # print(10 * userwidthlist[:-1])
    # print(10 * userwidthlist[1:])
    # print((spacesbetween > 10 * userwidthlist[:-1]) &
    #       (spacesbetween > 10 * userwidthlist[1:]))
    # print("splitindices:")
    # print(splitindices)
    # splitresonances = np.split(userposlist,splitindices[0]+1)
    splitparams = np.split(fullparamlist, 4 * (splitindices[0] + 1))
    # print("4*splitindices[0]+1:")
    # print(4 * (splitindices[0] + 1))
    # print("splitparams:")
    # print(splitparams)

    newparamlist = np.array([])

    # plt.plot(freq,R)

    # fit to each group of resonances separately
    for paramset in splitparams:

        paramset = paramsort(paramset)

        # lowest freq - 10*(lowest FWHM)
        freqmin = paramset[2] - 10 * paramset[3]
        # highest freq + 10*(highest FWHM)
        freqmax = paramset[-2] + 10 * paramset[-1]
        freqmax, freqmin = max(freqmax, freqmin), min(freqmax, freqmin)
        freqsubset = freq[(freq < freqmax) &
                          (freq > freqmin)]
        Rsubset = R[(freq < max(freqmax, freqmin)) &
                    (freq > min(freqmax, freqmin))]

        print("predicted frequency:")
        print(paramset[2])
        oldFreqs = paramset[0::1]

        if len(freqsubset) == 0:
            bugMe("yikes")
            print("totalMinFreq:")
            print("    " + str(totalMinFreq))
            print("totalMaxFreq:")
            print("    " + str(totalMaxFreq))
            print("freqsubset:")
            print("    " + str(freqsubset))
            print(" ")
            print("paramset:")
            print("    " + str(paramset))
            print(" ")
            print("freqmax:")
            print("    " + str(freqmax))
            print(" ")
            print("freqmin:")
            print("    " + str(freqmin))
            print(" ")
            print("freq:")
            print(str(min(freq)) + " - " + str(max(freq)))
            print(" ")
            # wait.sleep(5)
            # Plot the yikes point to see what's going on - dig into this
            # Try ignoring the super small widths
            peakidx = (np.abs(freq - paramset[3])).argmin()
            freqsubset = freq[peakidx - 3:peakidx + 3]
            print("Length of frequency subset:")
            print(len(freqsubset))
            freqmax = freqmax * 10
            freqmin = freqmin / 10
            freqmax, freqmin = max(freqmax, freqmin), min(freqmax, freqmin)
            Rsubset = R[(freq < max(freqmax, freqmin)) &
                        (freq > min(freqmax, freqmin))]
            peakidx = (np.abs(freq - paramset[3])).argmin()
            freqsubset = freq[peakidx - 3:peakidx + 3]
            # return paramset

        [slope, offset] = np.polyfit(freqsubset, Rsubset, deg=1)
        p0 = np.append(paramset, [offset, slope])
        print(" ")
        print("p0:")
        print("    offset:")
        print("        " + str(offset))
        print("    slope:")
        print("        " + str(slope))

        weights = np.ones(len(freqsubset))
        result = least_squares(multilorentzresidual, p0, ftol=1e-10,
                               args=(freqsubset, Rsubset, weights))
        params = result.x
        print("missedFrequencies:")
        print(params[2::4])
        oldFreqs = paramsort(oldFreqs)
        params = paramsort(params)
        for i in range(0, len(params[2::4])):
            params[i * 4 + 2] = checkFrequency(params[i * 4 + 2], oldFreqs[i * 4 + 2], totalMinFreq, totalMaxFreq)
        # don't bother storing params for background fit
        newparamlist = np.append(newparamlist, params[:-2])
        newparamlist = paramsort(newparamlist)
        # plt.plot(freqsubset,multilorentz(params,freqsubset),'r')

    # newpeakpositions = newparamlist[2::4]
    # np.savetxt('AG2439 - I - RPR - 3cooldown.txt',
    # newpeakpositions, delimiter=',')

    # plt.show()

    newparamlist = paramsort(newparamlist)

    bugMe("diagnostic")
    print("newparamlist:")
    print(str(newparamlist))

    return newparamlist


def cleanBadParams(params):
    global totalMinFreq
    global totalMaxFreq
    newParams = np.array([])
    positions = params[2::4]
    for i in range(0, len(positions)):
        if positions[i] < totalMinFreq or positions[i] > totalMaxFreq:
            positions[i] = False
        else:
            toAdd = np.array([params[i * 4], params[i * 4 + 1], params[i * 4 + 2], params[i * 4 + 3]])
            newParams = np.append(newParams, toAdd)
    return newParams

def trackpeaks(initparamlist, filepaths):
    # print("now calling trackpeaks")
    numlorentz = int(len(initparamlist) / 4)  # number of resonances
    # print("Number of resonances:")
    # print(len(initparamlist) / 4)
    peakpositions = np.zeros((numlorentz, len(filepaths)))
    # print("Peak Positions:")
    # print(peakpositions)
    peakwidths = np.zeros((numlorentz, len(filepaths)))
    # print("Peak Widths:")
    # print(peakwidths)
    starttemps = np.zeros(len(filepaths))
    # print("Start Temps:")
    # print(starttemps)

    for i in range(0, len(filepaths)):
        if i % 30 == 0:
            print(i)  # just to see progress
        [freq, X, Y, starttemp, endtemp] = returnvals(filepaths[i], 1, 0)
        R = sqrt(X ** 2 + Y ** 2)

        newparamlist = clusteredfits(freq, R, initparamlist)

        # take every 4th element, starting with #2
        peakpositions[:, i] = newparamlist[2::4]
        # take every 4th element, starting with #3
        peakwidths[:, i] = newparamlist[3::4]

        starttemps[i] = starttemp

        initparamlist = newparamlist

    for i in range(0, numlorentz):
        plt.plot(starttemps, peakpositions[i, :])

    plt.show()

def checkFrequency(thisFreq, backupFreq, minFreq, maxFreq):
    if thisFreq > maxFreq or thisFreq < minFreq:
        bugMe("crisis averted?")
        print("minFreq: " + str(minFreq))
        print("maxFreq: " + str(maxFreq))
        print("thisFreq: " + str(thisFreq))
        print("backupFreq: " + str(backupFreq))
        return backupFreq
    else:
        bugMe("no crisis?")
        print("thisFreq: " + str(thisFreq))
        return thisFreq


# unsuccessful attempts to find resonances purely via automated
# peak-finding rather than by eye
def findpeaks(filepath):
    # print("now calling findpeaks")
    [freq, X, Y, starttemp, endtemp] = returnvals(filepath, 1, 0)
    global totalpeaklist
    global totaltemplist

    R = sqrt(X ** 2 + Y ** 2)
    # plt.plot(freq,R,color='b')

    [maxes, mins] = peakdet(R, 0.00003, freq)
    peaklist = np.array([])
    for max in maxes:
        # plt.plot(max[0],max[1],'x',color='r')
        # plt.plot(starttemp,max[0],'x',color='r')
        peaklist = np.append(peaklist, max[0])
    for min in mins:
        peaklist = np.append(peaklist, min[0])

    # following line should be adjustable, depending on peakwidths/noise levels
    # peakind = signal.find_peaks_cwt(R,np.arange(10,100),min_snr=3)
    # peaklist = freqnew[peakind]
    # plt.plot(freq[peakind],R[peakind],'x')

    # use the find_peaks_cwt results as a starting point

    # for ind in peakind:
    # for i in range(1,len(peakind)):
    for i in range(0, len(peaklist)):
        #    #look at a window around the peak and try to fit it
        #    ind = peakind[i]
        ind = np.where(freq == peaklist[i])[0][0]
        freqsubset = freq[ind - 20:ind + 20]
        Rsubset = R[ind - 20:ind + 20]
        position = freq[ind]
        amplitude = np.amax(Rsubset) - np.amin(Rsubset)
        FWHM = 0.25 * (np.amax(freqsubset) - np.amin(freqsubset))
        [slope, offset] = np.polyfit(freqsubset, Rsubset, deg=1)
        p0 = [amplitude, -amplitude, position, FWHM, offset, slope]
        params, ier = leastsq(
            singlelorentzwithbgresidual, p0, args=(
                freqsubset, Rsubset))
    #   plt.plot(starttemp,params[1],'.',color='r')
        # plt.plot(freqsubset,Rsubset)
        # plt.plot(freqsubset,singlelorentzwithbg(params,freqsubset),'r')
        # plt.plot(starttemp,freqnew[ind],',',color='c')
        # plt.plot(starttemp,peaklist[i],',',color='c')
        plt.plot(starttemp, params[2], '.', color='c')
        # plt.show()

    starttempvec = starttemp * np.ones(len(peaklist))
    # plt.plot(starttempvec,peaklist,'.',color='c',markersize=2)

    totalpeaklist.append(peaklist)
    totaltemplist.append(starttemp)


def paramsort(p):
    newamplist = p[0::4]
    newskewlist = p[1::4]
    newposlist = p[2::4]
    newwidthlist = p[3::4]
    newsortedinds = newposlist.argsort()
    # newsortedinds = newsortedinds[::-1]
    sortednewamplist = newamplist[newsortedinds]
    sortednewskewlist = newskewlist[newsortedinds]
    sortednewposlist = newposlist[newsortedinds]
    sortednewwidthlist = newwidthlist[newsortedinds]
    updatedparamset = []
    for i in range(0, len(newposlist)):
        updatedparamset.append(sortednewamplist[i])
        updatedparamset.append(sortednewskewlist[i])
        updatedparamset.append(np.fabs(sortednewposlist[i]))
        updatedparamset.append(sortednewwidthlist[i])
    return p


# lorentzian (only peak; not absorptive)
def lorentz(p, x):
    # print("now calling lorentz")
    return p[0] / sqrt((p[1] ** 2 - x ** 2) ** 2 + p[2] ** 2 * x ** 2)


def lorentzresidual(p, x, z):
    # print("now calling lorentzresidual")
    return lorentz(p, x) - z


def lorentzwithbg(p, x):
    # print("now calling lorentzwithbg")
    return p[0] / sqrt((p[1] ** 2 - x ** 2) ** 2 + p[2] ** 2 * x ** 2) + p[3]


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
    return (p[0] + p[1] * (x - p[2])) / ((x - p[2]) ** 2 + 1 / 4 * p[3] ** 2)
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


if __name__ == '__main__':
    main()
