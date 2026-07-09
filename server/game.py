import dataSaving
from server.serverHTML.serverForWorldEditing import ServerHTML as ServerHTMLEditing
from server.serverHTML.server import ServerHTML as ServerHTMLReadOnly
import blockInfo
import os
import serverTCP

class Game:
    def __init__(self, worldSize):
        self.worldFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world.pkl")
        self.worldSize = worldSize
        self.world = []
        self.TCPserver = serverTCP.Server(("0.0.0.0", 65432))
        self.saver = dataSaving.DataSaving(self.worldFilePath)
        world = self.saver.loadWorld()
        if world:
            self.world = world
        else:
            self.createNewWorld()
            self.saver.saveWorld(self.world)

        self.initHTMLServer(serverType=True)
        
        self.webServer.startServer()

    def initHTMLServer(self, serverType):
        if serverType == True:
            self.webServer = ServerHTMLEditing(
                host="0.0.0.0", 
                port=5000, 
                getMapPart=self.getMapPart,
                blockChange=self.changeBlock,
                worldSize=self.worldSize,
                blockList=blockInfo.getBlockList()
            )
        else:
            self.webServer = ServerHTMLReadOnly(
                host="0.0.0.0",
                port=5000,
                getMapPart=self.getMapPart,
                worldSize=self.worldSize
            )

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

if __name__ == "__main__":
    game = Game(worldSize=1000)