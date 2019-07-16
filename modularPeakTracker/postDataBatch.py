from dataBatch import DataBatch

class PostDataBatch(DataBatch):
    def inheritData(self, dataBatch):
        self.freqData = dataBatch.freqData
        self.rData = dataBatch.rData
        self.startTemp = dataBatch.startTemp
        self.endTemp = dataBatch.endTemp
        self.searchTerms["freq"] = self.freqData
        self.searchTerms["r"] = self.rData
