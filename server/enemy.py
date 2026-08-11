import random
import data

class Enemy:
    def __init__(self, pos, entity, id, game):
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.myId = id
        self.game = game
        self.eDetails = entity

        self.dir = 'north'
        self.moveTargetX = float(self.x)
        self.moveTargetY = float(self.y)
        self.isMoving = False
        self.lastActionTime = 0
        self.lastAttackTime = 0
        self.offsets = {'north': (0, -1), 'east': (1, 0), 'south': (0, 1), 'west': (-1, 0)}
        self.startingPause = random.uniform(0.001, 1.001)

    def updatePhysics(self, deltaTime, currentTime):
        if not self.isMoving:
            return
        step = self.eDetails['speed'] * deltaTime

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
            self.lastActionTime = currentTime

    def takeDamage(self, dmg):
        self.eDetails['health'] -= dmg
        if self.eDetails['health'] <= 0.0:
            self.eDetails = data.getObjectInfo(self.eDetails['typeId'])
            newPos = self.game.getRandomPos(self.game.world[int(self.y)][int(self.x)]['zone'])
            self.game.updateEntityMovement((self.moveTargetX, self.moveTargetY), newPos, self.myId)
            self.isMoving = False
            self.x = newPos[0]
            self.y = newPos[1]
            return self.eDetails['drops']
        else:
            return None

    def move(self, currentTime):
        if self.isMoving or currentTime - self.lastActionTime < self.eDetails['walkPause'] + self.startingPause:
            return
        if self.lastActionTime != 0:
            self.startingPause = 0.0
        if self.eDetails['behavior'] == 'passive':
            self.passive()
        elif self.eDetails['behavior'] == 'aggressive':
            self.aggressive(currentTime)

    def canWalkOn(self, object):
        if object['block']['typeId'] in self.eDetails['allowedBlocks'] and object['entities'] == {}:
            return True
        return False

    def availableDirs(self, mapPart):
        mid = int(len(mapPart) / 2)
        possibleDirs = []
        
        for d in data.dirs:
            targetX = mid + self.offsets[d][0]
            targetY = mid + self.offsets[d][1]
            if 0 <= targetY < len(mapPart) and 0 <= targetX < len(mapPart[0]):
                if self.canWalkOn(mapPart[targetY][targetX]):
                    possibleDirs.append(d)
        return possibleDirs

    def passive(self):
        mapData = self.game.getMapPart(int(self.x) - 1, int(self.y) - 1, 3, 3)
        dirs = self.availableDirs(mapData)
        
        oppositeDir = data.dirs[(data.dirs.index(self.dir) + 2) % len(data.dirs)]
        if oppositeDir in dirs and len(dirs) != 1:
            dirs.remove(oppositeDir)
        dirs.append(None)
        moveChoice = random.choice(dirs)
        if moveChoice is not None:
            self.executeStep(moveChoice)            

    def aggressive(self, currentTime):
        sight = self.eDetails['sight']
        width = sight * 2 + 1
        mapData = self.game.getMapPart(int(self.x) - sight, int(self.y) - sight, width, width)
        
        targetX, targetY = None, None
        
        for rIdx, row in enumerate(mapData):
            for cIdx, cell in enumerate(row):
                if 'entities' in cell:
                    if cell['block']['typeId'] in self.eDetails['allowedBlocks']:
                        for entId, entObj in cell['entities'].items():
                            if entObj.__class__.__name__ == "Player":
                                targetX = int(self.x) - sight + cIdx
                                targetY = int(self.y) - sight + rIdx
                                break
            if targetX is not None:
                break

        if targetX is None:
            self.passive()
            return

        moveChoice = self.pathFind(mapData, targetX, targetY)
        if moveChoice == 'attack':
            self.attack(currentTime)
        elif moveChoice:
            self.executeStep(moveChoice)
        else:
            self.passive()
        
    def attack(self, currentTime):
        if currentTime - self.lastAttackTime < self.eDetails['attackPause']:
            return
        self.lastAttackTime = currentTime
        for entity in list(self.game.world[int(self.y) + self.offsets[self.dir][1]][int(self.x) + self.offsets[self.dir][0]]['entities'].values()):
            if entity.__class__.__name__ == 'Player':
                entity.takeDamage(self.eDetails['damage'])

    def pathFind(self, mapPart, targetX, targetY):
        sight = int(self.eDetails['sight'])
        width = len(mapPart)
        startC, startR = sight, sight
        targetC = int(targetX) - int(self.x) + sight
        targetR = int(targetY) - int(self.y) + sight
        queue = [(startR, startC, [])]
        visited = {(startR, startC)}
        while queue:
            r, c, path = queue.pop(0)
            for direction, (dx, dy) in self.offsets.items():
                if r + dy == targetR and c + dx == targetC:
                    if not path:
                        self.dir = direction
                        return 'attack'
                    else:
                        return path[0]
            for direction, (dx, dy) in self.offsets.items():
                nr, nc = r + dy, c + dx
                if 0 <= nr < width and 0 <= nc < width and (nr, nc) not in visited:
                    if self.canWalkOn(mapPart[nr][nc]):
                        visited.add((nr, nc))
                        queue.append((nr, nc, path + [direction]))
        return None

    def executeStep(self, moveChoice):
        oldX, oldY = int(self.x), int(self.y)
        newX = oldX + self.offsets[moveChoice][0]
        newY = oldY + self.offsets[moveChoice][1]
        self.moveTargetX = float(newX)
        self.moveTargetY = float(newY)
        self.dir = moveChoice
        self.isMoving = True
        self.game.updateEntityMovement((oldX, oldY), (newX, newY), self.myId)