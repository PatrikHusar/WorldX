import random
import data

class Entity:
    def __init__(self, pos, entity):
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.entity = entity
        self.allowedZone = self.entity['zone']
        self.damage = self.entity['properties']['damage']
        self.health = self.entity['properties']['health']
        self.speed = self.entity['properties']['speed']
        self.behaviour = self.entity['properties']['behavior']
        self.sight = self.entity['properties']['sight']
        self.pauseBetweenMoves = self.entity['properties']['pause']
        self.swimmingSkill = self.entity['properties']['swimmingSkill']

        self.dir = 'north'
        self.moveTargetX = float(self.x)
        self.moveTargetY = float(self.y)
        self.targetX = float(self.x)
        self.targetY = float(self.y)
        self.isMoving = False
        self.time = 0

    def updatePhysics(self, deltaTime, currentTime):
        if not self.isMoving:
            return
        step = self.speed * deltaTime

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

    def move(self, getMapPart, currentTime):
        if self.isMoving:
            return
        if not currentTime - self.time > self.pauseBetweenMoves:
            return
        self.time = currentTime
        if self.behaviour == 'passive':
            self.passive(getMapPart)
        elif self.behaviour == 'aggressive':
            self.aggressive(getMapPart)

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
                    if obj['zone'] in self.allowedZone and self.isWalkable(obj):
                        possibleDirs.append(direction)
        return possibleDirs
    
    def isWalkable(self, obj):
        walkable = obj['walkable']
        try:
            swimmable = obj['properties']['swimmable']
        except:
            pass
        if walkable == True:
            return True
        elif swimmable == False:
            return False
        elif swimmable <= self.swimmingSkill and walkable == False:
            return True
        else:
            return False

    # def getRandomLocalZonePos(self):
    #     targetX = int(self.x + random.randint(-self.sight, self.sight))
    #     targetY = int(self.y + random.randint(-self.sight, self.sight))
    #     if 0 <= targetX < self.worldSize and 0 <= targetY < self.worldSize:
    #         currentZone = self.world[targetY][targetX]['zone']
    #         if currentZone in self.allowedZone:
    #             return (targetX, targetY)
    #     return None
    def checkMap(self, map, key, value):
        objectList = []
        for r in map:
            for c in r:
                if c[key] == value:
                    objectList.append(c)
        return objectList
    def checkProperties(self, properties, obj):
        obj[properties]
        
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
            self.moveTargetX = float(newX)
            self.moveTargetY = float(newY)
            self.dir = moveChoice
            self.isMoving = True
    def neutral(self, getMapPart):
        mapData = getMapPart(int(self.x) - self.sight, int(self.y) - self.sight, self.sight * 2 + 1, self.sight * 2 + 1)
        mapData = data.transferIdMap(mapData)
    def aggressive(self, getMapPart):
        mapData = getMapPart(int(self.x) - self.sight, int(self.y) - self.sight, self.sight * 2 + 1, self.sight * 2 + 1)
        mapData = data.transferIdMap(mapData)
        players = self.checkMap(mapData, 'type', 'player')
        if not players:
            self.passive(getMapPart)
        else:
            pass