class Grave:
    def __init__(self, pos, grave, id, drops):
        self.myId = id
        self.x = pos[0]
        self.y = pos[1]
        self.eDetails = grave
        self.eDetails['inventory'] = drops
        self.dir = 'north'

    def claimGrave(self):
        return self.eDetails['inventory']