import modularLiveFit as fit
import modularConfig as conf
import numpy as np

def getFrequencies(dataBatch):
    allParameters = dataBatch.getAllParameters()
    frequencyParameters = allParameters[2::4]
    return frequencyParameters

def makeLorentzPairs(referenceLorentzList, targetLorentzList):
    referenceListLength = len(referenceLorentzList)
    targetListLength = len(targetLorentzList)
    finalListLength = max(referenceListLength, targetListLength)
    pairList = []
    if referenceListLength == targetListLength:
        for i in range(0, finalListLength):
            pairList.append((referenceLorentzList[i], targetLorentzList[i]))
    else:
        if targetListLength > referenceListLength:
            longLorentzList = list(targetLorentzList)
            shortLorentzList = list(referenceLorentzList)
        else:
            longLorentzList = list(referenceLorentzList)
            shortLorentzList = list(targetLorentzList)
        lorentzCompareValues = {}
        for lorentz in longLorentzList:
            closestLorentz = findClosestLorentz(lorentz, shortLorentzList)
            closestLorentzDistance = getPeakDistance(lorentz, closestLorentz)
            lorentzCompareValues[lorentz] = closestLorentzDistance
        badLorentzList = []
        while len(longLorentzList) != len(shortLorentzList):
            worstLorentz = max(lorentzCompareValues, key=lorentzCompareValues.get)
            longLorentzList.remove(worstLorentz)
            badLorentzList.append(worstLorentz)
        referenceOffset = 0
        targetOffset = 0
        for i in range(0, finalListLength):
            referenceLorentz = referenceLorentzList[i + referenceOffset]
            targetLorentz = targetLorentzList[i + targetOffset]
            if referenceLorentz in badLorentzList:
                pairList.append(referenceLorentz, None)
            elif targetLorentz in badLorentzList:
                pairList.append(None, targetLorentz)
            else:
                pairList.append(referenceLorentz, targetLorentz)
    return pairList

def findClosestLorentz(lorentz, lorentzList):
    bestLorentz = lorentzList[0]
    bestLorentzDistance = getPeakDistance(lorentz, bestLorentz)
    for newLorentz in lorentzList:
        newLorentzDistance = getPeakDistance(lorentz, newLorentz)
        if newLorentzDistance < bestLorentzDistance:
            bestLorentz = newLorentz
            bestLorentzDistance = newLorentzDistance
    return bestLorentz

def getPeakDistance(lorentzOne, lorentzTwo):
    distance = abs(lorentzOne.peakFrequency - lorentzTwo.peakFrequency)
    return distance

def sortLorentzList(lorentzList):
    return sorted(lorentzList, key=lambda lorentz: \
        lorentz.peakFrequency)

def noisePredictor(dataBatch):
    fitList = fit.getMultiFitData(dataBatch)
    lorentzList = dataBatch.groupLorentz()
    noiseArray = np.array([])
    for i in range(0, len(fitList)):
        xMin = min(dataBatch.getLorentz(lorentzList[i][0]).xData)
        xMax = max(dataBatch.getLorentz(lorentzList[i][len(lorentzList[i]) \
            - 1]).xData)
        minMax = (xMin, xMax)
        yBackground = dataBatch.getData(minMax, "point", "r", "freq")
        yFit = fitList[i][1]
        yNoise = yBackground - yFit
        noiseArray = np.append(noiseArray, yNoise)
    noiseLevel = conf.noiseFilterLevel * np.std(noiseArray)
    return noiseLevel