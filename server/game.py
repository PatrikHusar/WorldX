import dataSaving
# from serverHTML.serverForWorldEditing import ServerHTML as ServerHTMLEditing
# from serverHTML.server import ServerHTML as ServerHTMLReadOnly
import data
import os
# import serverTCP
from mapper import PygameMapper
import threading
import entity
import time

class Game:
    def __init__(self, worldSize):
        self.worldFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world.pkl")
        self.worldSize = worldSize
        self.world = []
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
        
        self.entities = []
        self.entities.append(entity.Entity(75, 60, data.getObjectInfo(4)))
        self.entities.append(entity.Entity(75, 59, data.getObjectInfo(18)))
        
        self.mapper = PygameMapper(
        getMapPart=self.getMapPart,
        blockChange=self.changeBlock,
        worldSize=self.worldSize,
        blockList=data.getObjectList('block'),
        idToName=data.idToName
        )
        
        threading.Thread(target=self.main, daemon=True).start()
        
        self.mapper.run()
        
        
        
        # self.initHTMLServer(serverType=0)
        
        # self.webServer.startServer()

    # def initHTMLServer(self, serverType):
    #     if serverType == 0:
    #         self.webServer = ServerHTMLEditing(
    #             host="0.0.0.0", 
    #             port=5000, 
    #             getMapPart=self.getMapPart,
    #             blockChange=self.changeBlock,
    #             worldSize=self.worldSize,
    #             blockList=blockInfo.getBlockList()
    #         )
    #     else:
    #         self.webServer = ServerHTMLReadOnly(
    #             host="0.0.0.0",
    #             port=5000,
    #             getMapPart=self.getMapPart,
    #             worldSize=self.worldSize
    #         )

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

if __name__ == "__main__":
    game = Game(worldSize=180)