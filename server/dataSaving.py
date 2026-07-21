import pickle

class DataSaving:
    def __init__(self, dataPath):
        self.dataPath = dataPath
    def saveData(self, data):
            with open(self.dataPath, "wb") as f:
                pickle.dump(data, f)
    def loadData(self):
        try:
            with open(self.dataPath, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None
