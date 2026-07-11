import dataSaving
# from serverHTML.server import ServerHTML
import data
import os
# import serverTCP
from mapper import PygameMapper
import threading
import entity
import time
import random

class Game:
    def __init__(self, worldSize):
        self.worldFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world.pkl")
        self.worldSize = worldSize
        self.world = []
        self.entities = []
        self.zonePositions = {}
        # self.TCPserver = serverTCP.Server(("0.0.0.0", 65432))
        self.saver = dataSaving.DataSaving(self.worldFilePath)
        world = self.saver.loadWorld()
        if world:
            self.world = world
            if len(self.world) <= worldSize:
                self.enlargeWorld()
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

        
        
        
        
        threading.Thread(target=self.main, daemon=True).start()
        
        self.mapper.run()
        # self.webServer.startServer()

    def initVars(self):
        # self.webServer = ServerHTML(
            # host="0.0.0.0",
            # port=5000,
            # getMapPart=self.getMapPart,
            # worldSize=self.worldSize
        # )
        
        self.mapper = PygameMapper(
        getMapPart=self.getMapPart,
        blockChange=self.changeBlock,
        worldSize=self.worldSize,
        blockList=data.getObjectList('block'),
        idToName=data.idToName
        )
        
        for r in range(self.worldSize):
            for c in range(self.worldSize):
                zoneName = self.world[r][c]['zone']
                if self.world[r][c]['id'] in data.spawnableBlocks:
                    if zoneName in self.zonePositions:
                        self.zonePositions[zoneName].append((c, r))
                    else:
                        self.zonePositions[zoneName] = [(c, r)]

    def spawnEntities(self):
        for zone in data.zones[0:5]:
            for _ in range(data.maxEnemiesInZone[zone]):
                self.entities.append(entity.Entity(self.entitySpawn[zone][0](zone), self.entitySpawn[zone][1]))

    def main(self):
        deltaTime = 0.01
        while True:
            currentTime = time.perf_counter()
            for ent in self.entities:
                ent.move(getMapPart=self.getMapPart, currentTime=currentTime)
                ent.updatePhysics(deltaTime=deltaTime, currentTime=currentTime)
            self.mapper.updateEntities(self.entities)
            time.sleep(deltaTime)

    def createNewWorld(self):
        self.world = []
        for r in range(self.worldSize):
            row = []
            for c in range(self.worldSize):
                row.append(data.getObjectInfo(0))
            self.world.append(row)
    def getMapPart(self, startX, startY, width, height):
        mapPart = []
        for r in range(startY, min(startY + height, self.worldSize)):
            row = []
            for c in range(startX, min(startX + width, self.worldSize)):
                row.append(self.world[r][c]['id'])
            mapPart.append(row)
        return mapPart
    def changeBlock(self, x, y, newId):
        if 0 <= x < self.worldSize and 0 <= y < self.worldSize:
            self.world[y][x] = data.getObjectInfo(newId)
            self.saver.saveWorld(self.world)
            return True
        return False
    def enlargeWorld(self):
        oldSize = len(self.world)
        for r in range(oldSize):
            while len(self.world[r]) < self.worldSize:
                self.world[r].append(data.getObjectInfo(0))
        
        while len(self.world) < self.worldSize:
            row = []
            for c in range(self.worldSize):
                row.append(data.getObjectInfo(0))
            self.world.append(row)
        self.saver.saveWorld(self.world)

    def getRandomPos(self, zone):
        return random.choice(self.zonePositions[zone])

if __name__ == "__main__":
    game = Game(worldSize=180)