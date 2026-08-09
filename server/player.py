import data

class Player:
    def __init__(self, pos, player, id, game, password):
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.dir = 'north'
        self.playerId = id
        self.isMoving = False
        self.player = player
        self.game = game
        self.password = password
        self.offsets = {'north': (0, -1), 'east': (1, 0), 'south': (0, 1), 'west': (-1, 0)}
        self.moveTargetX = float(self.x)
        self.moveTargetY = float(self.y)
        self.time = 0
        self.actions = []

    def equipItem(self, item, place):
        pass
    def storeItem(self, item):
        pass
    def takeItem(self, item):
        pass
    def interact(self, action=None):
        entities = self.game.world[int(self.y) + self.offsets[self.dir][1]][int(self.x) + self.offsets[self.dir][0]]['entities'].copy().values()
        if entities:
            for entity in entities:
                if entity.__class__.__name__ == 'Chest':
                    itemIds = entity.openChest()
                    for id in itemIds:
                        itemName = next((item['name'] for item in data.items if item['typeId'] == id), None)
                        if itemName:
                            if self.player['inventorySpace'] >= 1:
                                self.player['inventorySpace'] -= 1
                                self.player['inventory'].append(itemName)

    def restorePlayer(self, chestInventory, inventory, graves):
        self.player['chestInventory'] = chestInventory
        self.player['inventory'] = inventory
        self.player['graves'] = graves

    def turnTowards(self, currentTime, dir):
        if currentTime - self.time < self.player['pause'] or self.isMoving:
            return
        self.dir = dir

    def canWalkOn(self, object):
        noEntities = True
        for entity in object['entities'].values():
            if entity.__class__.__name__ == 'Chest':
                noEntities = False
                break
        if object['block']['typeId'] in self.player['allowedBlocks'] and noEntities == True:
            return True
        return False

    def forward(self, currentTime):
        if currentTime - self.time < self.player['pause'] or self.isMoving:
            return
        self.time = currentTime
        
        targetTileX = int(self.x + self.offsets[self.dir][0])
        targetTileY = int(self.y + self.offsets[self.dir][1])
        
        if self.game.checkIfInsideWorld(targetTileX, targetTileY, 1, 1):
            if self.canWalkOn(self.game.world[targetTileY][targetTileX]):
                self.executeStep()

    def turnLeft(self, currentTime):
        if currentTime - self.time < self.player['pause'] or self.isMoving:
            return
        self.dir = data.dirs[data.dirs.index(self.dir) - 1]

    def turnRight(self, currentTime):
        if currentTime - self.time < self.player['pause'] or self.isMoving:
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
        oldX, oldY = int(self.x), int(self.y)
        newX = oldX + self.offsets[self.dir][0]
        newY = oldY + self.offsets[self.dir][1]
        self.moveTargetX = float(newX)
        self.moveTargetY = float(newY)
        self.isMoving = True
        self.game.updateEntityMovement((oldX, oldY), (newX, newY), self.playerId)

    def doAction(self, currentTime):
        if currentTime - self.time < self.player['pause'] or self.isMoving:
            return
        if self.actions:
            act = self.actions.pop(0)
            if act == 'forward':
                self.forward(currentTime)
            elif act == 'left':
                self.turnLeft(currentTime)
            elif act == 'right':
                self.turnRight(currentTime)
            elif act.startswith('turnTo:'):
                self.turnTowards(currentTime, act[6:])
            elif act.startswith('interact:'):
                if act[9:] == 'None':
                    self.interact()
                else:
                    self.interact(act[9:])