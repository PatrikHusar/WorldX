import dataSaving
from serverHTML.server import ServerHTML
import blockInfo
import os

class Game:
    def __init__(self, worldSize):
        self.worldFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world.pkl")
        self.worldSize = worldSize
        self.world = []
        self.saver = dataSaving.DataSaving(self.worldFilePath)
        world = self.saver.loadWorld()
        if world:
            self.world = world
        else:
            self.createNewWorld()
            self.saver.saveWorld(self.world)

        self.server = ServerHTML(
            host="0.0.0.0", 
            port=5000, 
            getMapPart=self.getMapPart,
            blockChange=self.changeBlock,
            worldSize=self.worldSize,
            blockList=blockInfo.getBlockList()
        )
        self.server.startServer()

    def createNewWorld(self):
        self.world = []
        for r in range(self.worldSize):
            row = []
            for c in range(self.worldSize):
                row.append(blockInfo.getBlockInfo(0))
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
            self.world[y][x] = blockInfo.getBlockInfo(newId)
            self.saver.saveWorld(self.world)
            return True
        return False

hra = Game(worldSize=1000)