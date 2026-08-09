import data

class Chest:
    def __init__(self, pos, chest, id):
        self.x = pos[0]
        self.y = pos[1]
        self.chest = chest
        self.dir = 'north'
        self.chestId = id
    
    def remove(self):
        pass