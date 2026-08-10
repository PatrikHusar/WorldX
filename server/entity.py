import random
import data

class Entity:
    def __init__(self, pos, entity, id, game):
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.entityId = id
        self.game = game
        self.entity = entity

        self.dir = 'north'
        self.moveTargetX = float(self.x)
        self.moveTargetY = float(self.y)
        self.isMoving = False
        self.time = 0
        self.offsets = {'north': (0, -1), 'east': (1, 0), 'south': (0, 1), 'west': (-1, 0)}
        self.startingPause = random.uniform(0.001, 1.001)

    def updatePhysics(self, deltaTime, currentTime):
        if not self.isMoving:
            return
        step = self.entity['speed'] * deltaTime

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

    def takeDamage(self, dmg):
        self.entity['health'] -= dmg
        if self.entity['health'] <= 0.0:
            self.entity = data.getObjectInfo(self.entity['typeId'])
            newPos = self.game.getRandomPos(self.game.world[int(self.y)][int(self.x)]['zone'])
            self.game.updateEntityMovement((self.moveTargetX, self.moveTargetY), newPos, self.entityId)
            self.isMoving = False
            self.x = newPos[0]
            self.y = newPos[1]
            return self.entity['drops']
        else:
            return None

    def move(self, currentTime):
        if self.isMoving or currentTime - self.time < self.entity['walkPause'] + self.startingPause:
            return
        if self.time != 0:
            self.startingPause = 0.0
        if self.entity['behavior'] == 'passive':
            self.passive()
        elif self.entity['behavior'] == 'aggressive':
            self.aggressive()

    def canWalkOn(self, object):
        if object['block']['typeId'] in self.entity['allowedBlocks'] and object['entities'] == {}:
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

    def aggressive(self):
        sight = int(self.entity.get('sight', 3))
        width = sight * 2 + 1
        mapData = self.game.getMapPart(int(self.x) - sight, int(self.y) - sight, width, width)
        
        targetX, targetY = None, None
        
        for rIdx, row in enumerate(mapData):
            for cIdx, cell in enumerate(row):
                if 'entities' in cell:
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
        if moveChoice != True:
            if moveChoice:
                self.executeStep(moveChoice)
            else:
                self.passive()

    def pathFind(self, mapPart, targetX, targetY):
        sight = int(self.entity['sight'])
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
                    return path[0] if path else True
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
        self.game.updateEntityMovement((oldX, oldY), (newX, newY), self.entityId)