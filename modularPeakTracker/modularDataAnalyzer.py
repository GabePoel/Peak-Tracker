class ModularDataAnalyzer:
    def __init__(self, dataSet):
        self.dataSet = dataSet
        self.dataNumber = dataSet.dataNumber
        lastDataBatch = dataSet.getDataBatch(self.dataNumber, "post")
        self.lorentzNumber = lastDataBatch.lorentzCount
    
    def separateLorentzTrends():
        
class LorentzSet:
    def __init__(self, lorentzNumber, dataSet):
        temperatureArray = np.array([])