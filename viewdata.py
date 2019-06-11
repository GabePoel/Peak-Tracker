#/usr/bin/python -tt

from __future__ import division #makes division default to floats
import numpy as np
from numpy import sqrt
from nptdms import TdmsFile
import matplotlib.pyplot as plt

import time as wait

from scipy import signal
from scipy.optimize import least_squares
from scipy.optimize import leastsq

from peakdetect import peakdet

import glob #for searching directory
import os

userposlist = np.array([])
userwidthlist = np.array([])
useramplist = np.array([])
totalpeaklist = []
totaltemplist = []

def main():
    print("now calling main")
    prefix = "/Users/gabrielperko-engel/Box/RUS data/Sylvia/" #change file path as needed
    directories = [prefix + "CeCoIn5/AG1800 - I/2_cooldown/"]
    filepaths = []
    for directory in directories:
        filepaths = filepaths + sorted(glob.glob(directory + "*.tdms"))
    printfreq(filepaths)


#pull desired values from each TDMS file
def returnvals(filepath,cleanbool,plottype):
    # print("now calling returnvals")
    #plottype: 0 = peakplot; 1 = colorplot; 2 = tempplot

    #get just name of file, without directory or extension
    filename,ext = os.path.splitext(os.path.basename(filepath))
    date,time,starttemp,endtemp = filename.split("_")
    #date,time,starttemp = filename.split("_") (old filename format)
    starttemp = float(starttemp[:-1])
    endtemp = float(endtemp[:-1])

    tdms_file = TdmsFile(filepath)
    fchannel = tdms_file.object('Untitled','freq (Hz)')
    Xchannel = tdms_file.object('Untitled','X1 (V)')
    Ychannel = tdms_file.object('Untitled','Y1 (V)')
    cryochannel = tdms_file.object('Untitled','Cryostat temp (K)')
    #probechannel = tdms_file.object('Untitled','Probe temp (K)')
    freq = fchannel.data
    X = Xchannel.data
    Y = Ychannel.data
    cryotemp = cryochannel.data
    #probetemp = probechannel.data

    starttemp = cryotemp[0]
    endtemp = cryotemp[-1]

    if cleanbool == 1: #remove all columns that include NaNs
        fullsignal = np.stack((freq,X,Y)) #create an array with rows freq, X, and Y
        cleansignal = fullsignal[:,~np.isnan(fullsignal).any(axis=0)] #remove any columns that include at least one NaN

        freq = cleansignal[0]
        X = cleansignal[1]
        Y = cleansignal[2]

    else: #interpolate across all NaNs
        X = interpolatenans(X)
        Y = interpolatenans(Y)
        freq = interpolatenans(freq)

    R = sqrt(X**2 + Y**2)
    starttempvec = starttemp*np.ones(len(R))
    if plottype == 0: #peakplot
        return [freq,X,Y,starttemp,endtemp]
    elif plottype == 1: #colorplot
        return [freq/1000,starttempvec,R]
    elif plottype == 2: #tempplot
        return cryotemp


def printfreq(filepaths):
    for i in range(0,len(filepaths)):
        if i%30 == 0:
            print i #just to see progress
        [freq,X,Y,starttemp,endtemp] = returnvals(filepaths[i],1,0)
        R = sqrt(X**2 + Y**2)
        print([freq,X,Y,starttemp,endtemp])


def interpolatenans(inputarray):
    print("now calling interpolatenans")
    if np.isnan(inputarray).any(): #if array contains any NaNs, interpolate over them
        boolarray = ~np.isnan(inputarray)
        goodindices = boolarray.nonzero()[0]
        goodpoints = inputarray[~np.isnan(inputarray)]
        badindices = np.isnan(inputarray).nonzero()[0]
        inputarray[np.isnan(inputarray)] = np.interp(badindices,goodindices,goodpoints)
    return inputarray


if __name__ == '__main__':
    main()
