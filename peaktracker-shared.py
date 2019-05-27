#/usr/bin/python -tt

from __future__ import division #makes division default to floats
import numpy as np
from numpy import sqrt
from nptdms import TdmsFile
import matplotlib.pyplot as plt

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
    prefix = "/Users/sylviakl/Box/RUS data/Sylvia/"
    directories = [prefix + "CeCoIn5/AG1800 - I/2_cooldown/"]
    filepaths = []
    for directory in directories:
        filepaths = filepaths + sorted(glob.glob(directory + "*.tdms")) 
    initparamlist = initializearray(filepaths[0])
    trackpeaks(initparamlist,filepaths)


#pull desired values from each TDMS file
def returnvals(filepath,cleanbool,plottype):
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
        fullsignal = np.stack((freq,X,Y)) #create an array with rows freq, X,and Y
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


#get initial list of parameters from user
def initializearray(filepath):
    [freq,X,Y,starttemp,endtemp] = returnvals(filepath,1,0)
    R = sqrt(X**2 + Y**2)
    
    fig = plt.figure()
    plt.plot(freq,R,picker=5)

    #allows user to interactively input initial parameters for each resonance.
    #when user clicks, position of click is peak position; height and width of plot are used for FWHM and amplitude.
    def onpick(event):
        global userposlist
        global userwidthlist
        global useramplist
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        plt.plot(xdata[ind][0],ydata[ind][0],'x',color='r') #mark selected point
        fig.canvas.draw()
        userposlist = np.append(userposlist,xdata[ind][0]) #add position of peak to list
        left,right = plt.xlim()
        down,up = plt.ylim()
        userwidthlist = np.append(userwidthlist,(right-left)/2) #add approximation of FWHM to list
        useramplist = np.append(useramplist,(up-down)/2) #add approximation of amplitude to list


    fig.canvas.mpl_connect('pick_event',onpick)
    plt.show()

    #sort lists so they are in increasing order based on resonance position
    sortedinds = userposlist.argsort()
    userposlist_ordered = userposlist[sortedinds]
    userwidthlist_ordered = userwidthlist[sortedinds]
    useramplist_ordered = useramplist[sortedinds]
    
    fullparamlist = np.array([])
    for i in range (0,len(userposlist_ordered)):
        position = userposlist_ordered[i]
        FWHM = userwidthlist_ordered[i]
        amplitude = useramplist_ordered[i]
            
        #amplitude, skewness, position, FWHM
        params = [amplitude,-amplitude,position,FWHM]
        fullparamlist = np.append(fullparamlist,params)

    
    newparamlist = clusteredfits(freq,R,fullparamlist)
    return newparamlist


#fit each group of resonances using the multilorentz function
def clusteredfits(freq,R,fullparamlist):
    userposlist = fullparamlist[2::4]
    userwidthlist = fullparamlist[3::4]
    
    #split frequency spectrum into independent chunks of clustered resonances
    spacesbetween = userposlist[1:]-userposlist[:-1] #spaces between resonance peaks
    #split the peaks into groups as long as there is a space of more than 10*FWHM from the peaks on either side of the space
    splitindices = np.where((spacesbetween > 10*userwidthlist[:-1]) & (spacesbetween > 10*userwidthlist[1:]))
    #splitresonances = np.split(userposlist,splitindices[0]+1)
    splitparams = np.split(fullparamlist,4*(splitindices[0]+1))


    newparamlist = np.array([])

    
    #plt.plot(freq,R)
    
    #fit to each group of resonances separately
    for paramset in splitparams:
        freqmin = paramset[2]-10*paramset[3] #lowest freq - 10*(lowest FWHM)
        freqmax = paramset[-2]+10*paramset[-1] #highest freq + 10*(highest FWHM)
        
        freqsubset = freq[(freq < freqmax) & (freq > freqmin)]
        Rsubset = R[(freq < freqmax) & (freq > freqmin)]
        if len(freqsubset) == 0:
            print 'yikes'
            peakidx = (np.abs(freq - paramset[2])).argmin()
            freqsubset = freq[peakidx-3:peakidx+3]
            Rsubset = R[peakidx-3:peakidx+3]

            
        [slope,offset]=np.polyfit(freqsubset,Rsubset,deg=1)
        p0 = np.append(paramset,[offset,slope])
        
        weights = np.ones(len(freqsubset))
        result = least_squares(multilorentzresidual,p0,ftol=1e-10,args=(freqsubset,Rsubset,weights))
        params = result.x
        newparamlist = np.append(newparamlist,params[:-2]) #don't bother storing params for background fit
        #plt.plot(freqsubset,multilorentz(params,freqsubset),'r')

    #newpeakpositions = newparamlist[2::4]
    #np.savetxt('AG2439 - I - RPR - 3cooldown.txt',newpeakpositions,delimiter=',')
        
    #plt.show()

    return newparamlist


def trackpeaks(initparamlist,filepaths):
    numlorentz = int(len(initparamlist)/4) #number of resonances
    peakpositions = np.zeros((numlorentz,len(filepaths)))
    peakwidths = np.zeros((numlorentz,len(filepaths)))
    starttemps = np.zeros(len(filepaths))
    
    for i in range(0,len(filepaths)):
        if i%30 == 0:
            print i #just to see progress
        [freq,X,Y,starttemp,endtemp] = returnvals(filepaths[i],1,0)
        R = sqrt(X**2 + Y**2)
    
        newparamlist = clusteredfits(freq,R,initparamlist)
        
        peakpositions[:,i] = newparamlist[2::4] #take every 4th element, starting with #2
        peakwidths[:,i] = newparamlist[3::4] #take every 4th element, starting with #3
        
        starttemps[i] = starttemp
        
        initparamlist = newparamlist
        
    for i in range(0,numlorentz):
        plt.plot(starttemps,peakpositions[i,:])

    plt.show()


#unsuccessful attempts to find resonances purely via automated peak-finding rather than by eye
def findpeaks(filepath):
    [freq,X,Y,starttemp,endtemp] = returnvals(filepath,1,0)
    global totalpeaklist
    global totaltemplist
    
    R = sqrt(X**2 + Y**2)       
    #plt.plot(freq,R,color='b')
    
    [maxes,mins] = peakdet(R,0.00003,freq)
    peaklist = np.array([])
    for max in maxes:
        #plt.plot(max[0],max[1],'x',color='r')
        #plt.plot(starttemp,max[0],'x',color='r')
        peaklist = np.append(peaklist,max[0])
    for min in mins:
        peaklist = np.append(peaklist,min[0])

    #the following line needs to be adjustable, depending on peakwidths/noise levels
    #peakind = signal.find_peaks_cwt(R,np.arange(10,100),min_snr=3)
    #peaklist = freqnew[peakind]
    #plt.plot(freq[peakind],R[peakind],'x')

    #use the find_peaks_cwt results as a starting point

    #for ind in peakind:
    #for i in range(1,len(peakind)):
    for i in range(0,len(peaklist)):
    #    #look at a window around the peak and try to fit it
    #    ind = peakind[i]
        ind = np.where(freq == peaklist[i])[0][0]
        freqsubset = freq[ind-20:ind+20]
        Rsubset = R[ind-20:ind+20]
        position = freq[ind]
        amplitude = np.amax(Rsubset)-np.amin(Rsubset)
        FWHM = 0.25*(np.amax(freqsubset)-np.amin(freqsubset))
        [slope,offset]=np.polyfit(freqsubset,Rsubset,deg=1)
        p0 = [amplitude,-amplitude,position,FWHM,offset,slope]
        params,ier = leastsq(singlelorentzwithbgresidual,p0,args=(freqsubset,Rsubset))
    #   plt.plot(starttemp,params[1],'.',color='r')
        #plt.plot(freqsubset,Rsubset)
        #plt.plot(freqsubset,singlelorentzwithbg(params,freqsubset),'r')
        #plt.plot(starttemp,freqnew[ind],',',color='c')
        #plt.plot(starttemp,peaklist[i],',',color='c')
        plt.plot(starttemp,params[2],'.',color='c')
        #plt.show()

    starttempvec = starttemp*np.ones(len(peaklist))
    #plt.plot(starttempvec,peaklist,'.',color='c',markersize=2)

    totalpeaklist.append(peaklist)
    totaltemplist.append(starttemp)
    


#lorentzian (only peak; not absorptive)
def lorentz(p,x):
    return p[0]/sqrt((p[1]**2 - x**2)**2+p[2]**2*x**2)
def lorentzresidual(p,x,z):
    return lorentz(p,x)-z
def lorentzwithbg(p,x):
    return p[0]/sqrt((p[1]**2 - x**2)**2+p[2]**2*x**2) + p[3]
def lorentzwithbgresidual(p,x,z):
    return lorentzwithbg(p,x)-z

#p: fit parameters; x: frequencies; z: data
def singlelorentz(p,x):
    return (p[0]+p[1]*(x-p[2]))/((x-p[2])**2+1/4*p[3]**2) #using Lorentzian form from Zadler's paper
def singlelorentzresidual(p,x,z):
    return singlelorentz(p,x)-z
def multilorentz(p,x):
    m = p[-1]
    b = p[-2]
    numlorentz = int((len(p)-2)/4)
    result = m*x+np.ones(len(x))*b
    for i in range (0,numlorentz):
        params = p[i*4:i*4+4]
        #amplitude, skewness, position, FWHM
        #penalize positions outside freq range, as well as negative FWHM
        result = result + singlelorentz(params,x)
        if params[2] < x[0]:
            result = result + x*1000000
        if params[2] > x[-1]:
            result = result + x*1000000
        if params[3] < 0:
            result = result + x*1000000
    return result
def multilorentzresidual(p,x,z,weights):
    return (multilorentz(p,x) - z)*weights
def singlelorentzwithbg(p,x):
    return (p[0]+p[1]*(x-p[2]))/((x-p[2])**2+1/4*p[3]**2)+p[4]+x*p[5]
def singlelorentzwithbgresidual(p,x,z):
    return singlelorentzwithbg(p,x)-z

def anharmonic(p,x):
    return p[0]-p[1]/(np.exp(p[2]/x)-1)
def anharmonicresidual(p,x,z,weights):
    return (anharmonic(p,x)-z)*weights


def interpolatenans(inputarray):
    if np.isnan(inputarray).any(): #if array contains any NaNs, interpolate over them
        boolarray = ~np.isnan(inputarray)
        goodindices = boolarray.nonzero()[0]
        goodpoints = inputarray[~np.isnan(inputarray)]
        badindices = np.isnan(inputarray).nonzero()[0]
        inputarray[np.isnan(inputarray)] = np.interp(badindices,goodindices,goodpoints)
    return inputarray

        
if __name__ == '__main__':
    main()
