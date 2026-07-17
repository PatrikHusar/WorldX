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

    def move(self, currentTime):
        if self.isMoving == True or currentTime - self.time < self.entity['pause'] + self.startingPause:
            return
        if self.time != 0:
            self.startingPause = 0.0
        if self.entity['behavior'] == 'passive':
            self.passive()
        elif self.entity['behavior'] == 'aggressive':
            self.aggressive()

    def canWalkOn(self, object):
        if object['block']['id'] in self.entity['allowedBlocks']:
            return True
        return False

    def availableDirs(self, mapPart):
        mid = int(len(mapPart) / 2)
        possibleDirs = []
        directions = {}
        for dir in data.dirs:
            directions[dir] = (mid + self.offsets[dir][0], mid + self.offsets[dir][1])
        for dir in directions.keys():
            if self.canWalkOn(mapPart[directions[dir][1]][directions[dir][0]]):
                possibleDirs.append(dir)
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
        width = self.entity['sight'] * 2 + 1
        mapData = self.game.getMapPart(int(self.x) - self.entity['sight'], int(self.y) - self.entity['sight'], width, width)
        
        playerCell = None
        targetX, targetY = 0, 0
        
        for rIdx, row in enumerate(mapData):
            for cIdx, object in enumerate(row):
                if object['entities'].get('type') == 'player':
                    playerCell = object['object']
                    targetX = int(self.x) - self.entity['sight'] + cIdx
                    targetY = int(self.y) - self.entity['sight'] + rIdx

        if not playerCell:
            self.passive()
            return

        moveChoice = self.pathFind(mapData, targetX, targetY)
        if moveChoice:
            self.executeStep(moveChoice)
        else:
            self.passive()

    def pathFind(self, mapPart, targetX, targetY):
        sight = self.entity['sight']
        startX, startY = int(self.x), int(self.y)
        width = len(mapPart)
        
        startC, startR = sight, sight
        targetC = int(targetX) - startX + sight
        targetR = int(targetY) - startY + sight
        
        queue = [(startR, startC, [])]
        visited = {(startR, startC)}
        directions = {'north': (-1, 0), 'south': (1, 0), 'east': (0, 1), 'west': (0, -1)}
        
        while queue:
            r, c, path = queue.pop(0)
            if r == targetR and c == targetC:
                return path[0] if path else None
                
            for direction, (dr, dc) in directions.items():
                nr, nc = r + dr, c + dc
                if 0 <= nr < width and 0 <= nc < width and (nr, nc) not in visited:
                    if (nr == targetR and nc == targetC) or self.canWalkOn(mapPart[nr][nc]):
                        visited.add((nr, nc))
                        queue.append((nr, nc, path + [direction]))
        return None

    def executeStep(self, moveChoice):
        newX, newY = self.x, self.y
        for offset in self.offsets:
            if moveChoice == offset:
                newX += self.offsets[offset][0]
                newY += self.offsets[offset][1]     
        self.moveTargetX = float(newX)
        self.moveTargetY = float(newY)
        self.dir = moveChoice
        self.isMoving = True
        self.game.updateEntityMovement((self.x, self.y), (newX, newY), self.entityId)