import dataSaving
from serverHTML.serverHTML import ServerHTML
import data
# from player import Player
# import serverTCP
# from mapper import PygameMapper
import threading
from entity import Entity
import time
import random

class Game:
    def __init__(self):
        self.world = []
        self.zonePositions = {}
        self.entitiesPos = {}
        # self.TCPserver = serverTCP.Server(("0.0.0.0", 65432))
        self.saver = dataSaving.DataSaving(data.worldFilePath)
        world = self.saver.loadWorld()
        if world:
            self.world = world
            # self.delOldEntities()
        else:
            self.createNewWorld()
            self.saver.saveWorld(self.world)

        self.initVars()
        self.entitySpawn = {
            'forest': (self.getRandomPos, data.getObjectInfo(4)),
            'tundra': (self.getRandomPos, data.getObjectInfo(5)),
            'swamp': (self.getRandomPos, data.getObjectInfo(18)),
            'desert': (self.getRandomPos, data.getObjectInfo(23)),
            'volcano': (self.getRandomPos, data.getObjectInfo(24))
        }
        self.spawnEntities()
        # self.player = Player((50, 75))
        
        threading.Thread(target=self.main, daemon=True).start()
        
        self.webServer.startServer()

    def initVars(self):
        self.webServer = ServerHTML(
            host="0.0.0.0",
            port=5000,
            getMapPart=self.getMapPart,
            worldSize=data.worldSize,
            blockList=data.getObjectList('block')
        )
        self.initZonePositions()


    def initZonePositions(self):
        for y in range(data.worldSize):
            for x in range(data.worldSize):
                zoneName = self.world[y][x]['zone']
                if self.world[y][x]['block']['id'] in data.spawnableBlockIds:
                    if zoneName in self.zonePositions:
                        self.zonePositions[zoneName].append((x, y))
                    else:
                        self.zonePositions[zoneName] = [(x, y)]

    def spawnEntities(self):
        id = 0
        for zone in data.zones:
            zoneType = zone['zone']
            for _ in range(data.maxEnemiesInZone[zoneType]):
                self.entitiesPos[id] = self.entitySpawn[zoneType][0](zoneType)
                entity = Entity(self.entitiesPos[id], self.entitySpawn[zoneType][1], id, self)
                self.world[int(entity.y)][int(entity.x)]['entities'][entity.entityId] = entity
                id += 1

    def main(self):
        deltaTime = 0.01
        self.entities = self.getEntitiesList()
        lastUpdate = 0
        updateInterval = 0.05
        while True:
            currentTime = time.perf_counter()
            for ent in self.entities:
                ent.move(currentTime=currentTime)
                ent.updatePhysics(deltaTime=deltaTime, currentTime=currentTime)        
            if currentTime - lastUpdate >= updateInterval:
                self.webServer.updateEntities()
                lastUpdate = currentTime
            time.sleep(deltaTime)

    def delOldEntities(self):
        for row in self.world:
            for object in row:
                if object['entities']:
                    object['entities'] = {}
    
    def getEntitiesList(self):
        entities = []
        for id in self.entitiesPos:
            entities.append(self.world[self.entitiesPos[id][1]][self.entitiesPos[id][0]]['entities'][id])
        return entities
    
    def checkIfInsideWorld(self, startX, startY, width, height):
        if 0 <= startX <= data.worldSize - width and 0 <= startY <= data.worldSize - height:
            return True
        return False

    def updateEntityMovement(self, oldPos, newPos, id):
        self.world[int(newPos[1])][int(newPos[0])]['entities'][id] = self.world[int(oldPos[1])][int(oldPos[0])]['entities'][id]
        del self.world[int(oldPos[1])][int(oldPos[0])]['entities'][id]

    def createNewWorld(self):
        self.world = []
        for r in range(data.worldSize):
            row = []
            for c in range(data.worldSize):
                row.append(data.zones[0])
            self.world.append(row)
    def getMapPart(self, startX, startY, width, height):
        mapPart = []
        for r in range(startY, min(startY + height, data.worldSize)):
            row = []
            for c in range(startX, min(startX + width, data.worldSize)):
                row.append(self.world[r][c])
            mapPart.append(row)
        return mapPart

#     def changeBlock(self, x, y, newId):
#         if self.checkIfInsideWorld(x, y, 0, 0):
#             self.world[y][x] = data.getObjectInfo(newId)
#             self.saver.saveWorld(self.world)
#             return True
#         return False
#     def enlargeWorld(self):
#         oldSize = len(self.world)
#         for r in range(oldSize):
#             while len(self.world[r]) < data.worldSize:
#                 self.world[r].append(data.getObjectInfo(0))
#         while len(self.world) < data.worldSize:
#             row = []
#             for c in range(data.worldSize):
#                 row.append(data.getObjectInfo(0))
#             self.world.append(row)
#         self.saver.saveWorld(self.world)

    def getRandomPos(self, zone):
        return random.choice(self.zonePositions[zone])

if __name__ == "__main__":
    game = Game()