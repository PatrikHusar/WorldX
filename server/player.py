import data

class Player:
    def __init__(self, pos, player, id, game, name):
        self.x = int(pos[0])
        self.y = int(pos[1])
        self.dir = 'north'
        self.playerId = id
        self.isMoving = False
        self.player = player
        self.game = game
        self.name = name
        self.offsets = {'north': (0, -1), 'east': (1, 0), 'south': (0, 1), 'west': (-1, 0)}
        self.moveTargetX = float(self.x)
        self.moveTargetY = float(self.y)
        self.time = 0
        self.actions = []
        
        self.game.playersPos[id] = (self.x, self.y)
        self.game.world[self.y][self.x]['entities'][self.playerId] = self

    def equipItem(self, item, place):
        pass
    def storeItem(item):
        pass
    def takeItem(item):
        pass
    def restorePlayer(self, chestInventory, inventory, graves, name):
        self.chestInventory = chestInventory
        self.inventory = inventory
        self.player['inventory'] = inventory
        self.player['graves'] = graves
        self.name = name
    def turnTowards(self, dir):
        self.dir = dir
    def canWalkOn(self, object):
        if object['block']['id'] in self.player['allowedBlocks']:
            return True
        return False
    def forward(self, currentTime):
        if currentTime - self.time < self.player['pause'] or self.isMoving == True:
            return
        self.time = currentTime
        if self.canWalkOn(self.game.world[int(self.y + self.offsets[self.dir][1])][int(self.x + self.offsets[self.dir][0])]):
            self.executeStep()
    def turnLeft(self, currentTime):
        if currentTime - self.time < self.player['pause'] or self.isMoving == True:
            return
        self.dir = data.dirs[data.dirs.index(self.dir) - 1]
    def turnRight(self, currentTime):
        if currentTime - self.time < self.player['pause'] or self.isMoving == True:
            return
        self.dir = data.dirs[(data.dirs.index(self.dir) + 1) % 4]
    
    def updatePhysics(self, deltaTime, currentTime):
        if not self.isMoving:
            return
        step = self.player['speed'] * deltaTime

        if self.x < self.moveTargetX:
            self.x = min(self.moveTargetX, self.x + step)
        elif self.x > self.moveTargetX:
            self.x = max(self.moveTargetX, self.x - step)

        if self.y < self.moveTargetY:
            self.y = min(self.moveTargetY, self.y + step)
        elif self.y > self.moveTargetY:
            self.y = max(self.moveTargetY, self.y - step)

        if self.x == self.moveTargetX and self.y == self.moveTargetY:
            self.isMoving = False
            self.time = currentTime

    def executeStep(self):
        newX, newY = self.x, self.y
        newX += self.offsets[self.dir][0]
        newY += self.offsets[self.dir][1]     
        self.moveTargetX = float(newX)
        self.moveTargetY = float(newY)
        self.isMoving = True
        self.game.updateEntityMovement((self.x, self.y), (newX, newY), self.playerId)
    
    def doAction(self, currentTime):
        if len(self.actions) != 0:
            if self.actions[0] == 'forward':
                self.forward(currentTime)
                del self.actions[0]
            elif self.actions[0] == 'left':
                self.turnLeft(currentTime)
                del self.actions[0]
            elif self.actions[0] == 'right':
                self.turnRight(currentTime)
                del self.actions[0]