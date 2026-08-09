import data

class Chest:
    def __init__(self, pos, chest, id, game):
        self.x = pos[0]
        self.y = pos[1]
        self.chest = chest
        self.dir = 'north'
        self.chestId = id
        self.game = game
    
    def openChest(self):
        newPos = self.game.getRandomPos(self.game.world[self.y][self.x]['zone'])
        self.game.updateEntityMovement((self.x, self.y), newPos, self.chestId)
        self.x = newPos[0]
        self.y = newPos[1]
        return self.chest['drops']