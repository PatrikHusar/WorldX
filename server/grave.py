import inventory

class Grave:
    def __init__(self, pos, grave, id, drops):
        self.myId = id
        self.x = pos[0]
        self.y = pos[1]
        self.eDetails = grave
        inventory.setInventory(self, drops)
        self.dir = 'north'

    def claimGrave(self):
        return inventory.getInventory(self)