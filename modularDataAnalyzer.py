import numpy as np
import modularConfig as conf

class ModularDataAnalyzer:
    def __init__(self, parent):
        self.parent = parent
        self.fig = parent.fig
        self.ax = parent.ax
        self.canvas = parent.canvas
        self.dataSet = parent.dataSet
        self.dataNumber = parent.dataSet.dataNumber - 1
        lastDataBatch = self.dataSet.getDataBatch(self.dataNumber, "post")
        self.lorentzNumber = lastDataBatch.lorentzCount
        self.fullDataTable = None
        self.usefulDataTable = None
        self.simpleDataTable = None

    def createSimpleDataTable(self, includeHeader=True):
        titleArray = np.array([['Start Temperature']])
        tempArray = np.array([[]])
        freqArrayList = []
        for i in range(0, self.lorentzNumber):
            freqArrayList.append(np.array([[]]))
            titleArray = np.append(titleArray, np.array([['Lorentz ' + str(i) + \
                ' Peak Frequency']]))
        for dataBatch in self.dataSet.dataBatchArray:
            newTemp = np.array([[dataBatch.startTemp]])
            tempArray = np.append(tempArray, newTemp)
            for i in range(0, self.lorentzNumber):
                newFreq = np.array([[dataBatch.getLorentz(i).peakFrequency]])
                freqArrayList[i] = np.append(freqArrayList[i], newFreq)
        dataArray = tempArray
        for i in range(0, self.lorentzNumber):
            dataArray = np.vstack((dataArray, freqArrayList[i]))
        dataArray = np.transpose(dataArray)
        dataArray = np.vstack((titleArray, dataArray))
        self.simpleDataTable = dataArray
        return dataArray
    
    def createArrayFromLorentz(self, index, includeHeader=True):
        if includeHeader:
            arrayHeaders = np.array([['Lorentz ID', 'Start Temperature', \
                'Peak Frequency', 'Full Width Half Maximum', 'Skew', 'Amplitude',
                'Fit Cost']])
        else:
            arrayHeaders = None
        dataTable = arrayHeaders
        for dataBatch in self.dataSet.dataBatchArray:
            lorentz = dataBatch.getLorentz(index)
            dataArray = np.array([[index, dataBatch.startTemp, \
                lorentz.peakFrequency, lorentz.fullWidthHalfMaximum, 
                lorentz.skew, lorentz.amplitude, lorentz.fitCost]])
            if dataTable is None:
                dataTable = dataArray
            else:
                dataTable = np.append(dataTable, dataArray, axis=0)
        return dataTable

    def createFullDataTable(self, includeHeader=False):
        dataTable = [self.createArrayFromLorentz(0, includeHeader)]
        usefulTable = [self.createArrayFromLorentz(0, False)]
        for i in range(1, self.lorentzNumber):
            newFullData = self.createArrayFromLorentz(i, includeHeader)
            newUsefulData = self.createArrayFromLorentz(i, False)
            dataTable.append(newFullData)
            usefulTable.append(newUsefulData)
        self.fullDataTable = dataTable
        self.usefulDataTable = usefulTable
        return dataTable

    def plotDataTable(self):
        self.ax.cla()
        for i in range(0, self.lorentzNumber):
            xValues = self.getPlotValues(i)[0]
            yValues = self.getPlotValues(i)[1]
            self.ax.plot(xValues, yValues)
        self.canvas.draw()
        
    def getPlotValues(self, index):
        miniDataTable = self.usefulDataTable[index]
        return np.transpose(miniDataTable[:,[1, 2]])