import random
import data

class Entity:
    def __init__(self, x, y, entity):
        self.x = float(x)
        self.y = float(y)
        self.entity = entity
        self.allowedZone = self.entity['zone']
        self.damage = self.entity['properties']['damage']
        self.health = self.entity['properties']['health']
        self.speed = self.entity['properties']['speed']
        self.behaviour = self.entity['properties']['behavior']
        self.sight = self.entity['properties']['sight']
        self.pauseBetweenMoves = self.entity['properties']['pause']

        self.dir = 'north'
        self.targetX = float(x)
        self.targetY = float(y)
        self.isMoving = False
        self.time = 0

    def updatePhysics(self, deltaTime, currentTime):
        if not self.isMoving:
            return
        step = self.speed * deltaTime

        if self.x < self.targetX:
            self.x = min(self.targetX, self.x + step)
        elif self.x > self.targetX:
            self.x = max(self.targetX, self.x - step)

        if self.y < self.targetY:
            self.y = min(self.targetY, self.y + step)
        elif self.y > self.targetY:
            self.y = max(self.targetY, self.y - step)

        if self.x == self.targetX and self.y == self.targetY:
            self.isMoving = False
            self.time = currentTime

    def move(self, getMapPart, currentTime):
        if self.isMoving:
            return
        if not currentTime - self.time > self.pauseBetweenMoves:
            return
        self.time = currentTime
        if self.behaviour == 'passive':
            self.passive(getMapPart)
        elif self.behaviour == 'neutral':
            self.neutral(getMapPart)

    def availableDirs(self, mapPart):
        mid = int(len(mapPart) / 2)
        possibleDirs = []
        directions = {
            'north': (mid - 1, mid),
            'east':  (mid, mid + 1),
            'south': (mid + 1, mid),
            'west':  (mid, mid - 1)
        }
        for direction in data.dirs:
            if direction in directions:
                r, c = directions[direction]
                if 0 <= r < len(mapPart) and 0 <= c < len(mapPart[0]):
                    obj = mapPart[r][c]
                    if obj['zone'] in self.allowedZone and obj['walkable'] == True:
                        possibleDirs.append(direction)
        return possibleDirs
    
    def turnRight(self):
        pass

    def turnLeft(self):
        pass
    
    def passive(self, getMapPart):
        mapData = getMapPart(int(self.x) - 1, int(self.y) - 1, 3, 3)
        mapData = data.transferIdMap(mapData)
        dirs = self.availableDirs(mapData)
        if data.dirs[(data.dirs.index(self.dir) + 2) % len(data.dirs)] in dirs and len(dirs) != 1:
            dirs.remove(data.dirs[(data.dirs.index(self.dir) + 2) % len(data.dirs)])
        dirs.append(None)
        moveChoice = random.choice(dirs)
        if moveChoice is not None:
            newX, newY = self.x, self.y
            if moveChoice == 'north': newY -= 1
            elif moveChoice == 'south': newY += 1
            elif moveChoice == 'east': newX += 1
            elif moveChoice == 'west': newX -= 1
            diff = (data.dirs.index(moveChoice) - data.dirs.index(self.dir)) % 4
            if diff == 1 or diff == 2:
                self.turnRight()
            elif diff == 3:
                self.turnLeft()
            self.targetX = float(newX)
            self.targetY = float(newY)
            self.dir = moveChoice
            self.isMoving = True
    def neutral(self, getMapPart):
        mapPart = getMapPart(int(self.x) - self.sight, int(self.y) - self.sight, self.sight * 2 + 1, self.sight * 2 + 1)