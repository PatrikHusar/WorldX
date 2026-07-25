import dataSaving
from serverHTML.serverHTML import ServerHTML
import data
from player import Player
import serverTCP
from mapper import PygameMapper
import threading
from entity import Entity
import time
import random

class Game:
    def __init__(self):
        self.world = []
        self.zonePositions = {}
        self.entitiesPos = {}
        self.playersPos = {}
        self.idCounter = 0
        self.adressToPassword = {}
        self.worldSaver = dataSaving.DataSaving(data.worldFilePath)
        world = self.worldSaver.loadData()
        if world:
            self.world = world
            # self.delOldEntities()
        else:
            self.createNewWorld()
            self.worldSaver.saveData(self.world)
        self.playerSaver = dataSaving.DataSaving(data.playersFilePath)
        # self.restorePlayers()
        self.TCPserver = serverTCP.Server(("0.0.0.0", 65432), self.processClientData)
        self.webServer = ServerHTML(host="0.0.0.0", port=5000, game=self)
        self.initZonePositions()
        self.entitySpawn = {
            'forest': (self.getRandomPos, data.getObjectInfo(4)),
            'tundra': (self.getRandomPos, data.getObjectInfo(5)),
            'swamp': (self.getRandomPos, data.getObjectInfo(18)),
            'desert': (self.getRandomPos, data.getObjectInfo(23)),
            'volcano': (self.getRandomPos, data.getObjectInfo(24))
        }
        self.spawnEntities()
        threading.Thread(target=self.main, daemon=True).start()
        self.webServer.startServer()
    
    def createNewPlayer(self, password):
        player = Player(data.spawnPos, data.getObjectInfo(27), self.idCounter, self, password)
        self.idCounter += 1
        # self.savePlayer(player)

    def restorePlayers(self):
        players = self.playerSaver.loadData()
        if players == None:
            return
        for playerPassword in players:
            playerRestoreValues = players[playerPassword]
            player = Player(data.spawnPos, data.getObjectInfo(27), self.idCounter, self, '')
            player.restorePlayer(playerRestoreValues['chestInventory'], playerRestoreValues['inventory'], playerRestoreValues['graves'], playerPassword)
            self.idCounter += 1

    def savePlayer(self, player):
        playerData = {}
        saveData = {}
        saveData['chestInventory'] = player.player['chestInventory']
        saveData['inventory'] = player.player['inventory']
        saveData['graves'] = player.player['graves']
        playerData[player.password] = saveData
        self.playerSaver.saveData(playerData)

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
        for zone in data.zones:
            zoneType = zone['zone']
            for _ in range(data.maxEnemiesInZone[zoneType]):
                self.entitiesPos[self.idCounter] = self.entitySpawn[zoneType][0](zoneType)
                entity = Entity(self.entitiesPos[self.idCounter], self.entitySpawn[zoneType][1], self.idCounter, self)
                self.world[int(entity.y)][int(entity.x)]['entities'][entity.entityId] = entity
                self.idCounter += 1

    def main(self):
        deltaTime = 0.01
        entities = self.getEntitiesList()
        lastUpdate = 0
        updateInterval = 0.05
        while True:
            currentTime = time.perf_counter()
            for ent in entities:
                ent.move(currentTime=currentTime)
                ent.updatePhysics(deltaTime, currentTime)
            players = self.getPlayersList()
            for player in players:
                player.doAction(currentTime)
                player.updatePhysics(deltaTime, currentTime)
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
        for id in self.entitiesPos.keys():
            entities.append(self.world[self.entitiesPos[id][1]][self.entitiesPos[id][0]]['entities'][id])
        return entities
    def getPlayersList(self):
        players = []
        for id in self.playersPos.keys():
            players.append(self.world[self.playersPos[id][1]][self.playersPos[id][0]]['entities'][id])
        return players

    def checkIfInsideWorld(self, startX, startY, width, height):
        if 0 <= startX <= data.worldSize - width and 0 <= startY <= data.worldSize - height:
            return True
        return False

    def updateEntityMovement(self, oldPos, newPos, id):
        oldX, oldY = int(oldPos[0]), int(oldPos[1])
        newX, newY = int(newPos[0]), int(newPos[1])
        if id in self.world[oldY][oldX]['entities']:
            entityObj = self.world[oldY][oldX]['entities'].pop(id)
            self.world[newY][newX]['entities'][id] = entityObj
            if entityObj.__class__.__name__ == "Entity":
                self.entitiesPos[id] = (newX, newY)
            else:
                self.playersPos[id] = (newX, newY)
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
    def getPlayerByPassword(self, password):
        for player in self.getPlayersList():
            if player.password == password:
                return player
    def processClientData(self, playerMessage, adress):
        if adress in self.adressToPassword:
            if playerMessage.startswith(tuple(['forward', 'left', 'right', 'turnTo:'])):
                self.getPlayerByPassword(self.adressToPassword[adress]).actions.append(playerMessage)
            else:
                if playerMessage.startswith('getPos'):
                    player = self.getPlayerByPassword(self.adressToPassword[adress])
                    return (player.x, player.y)
        else:
            if playerMessage.startswith('login:'):
                password = playerMessage[6:]
                self.adressToPassword[adress] = password
                self.createNewPlayer(password)
        return 'ok'
#     def changeBlock(self, x, y, newId):
#         if self.checkIfInsideWorld(x, y, 0, 0):
#             self.world[y][x] = data.getObjectInfo(newId)
#             self.saver.saveWorld(self.world)
#             return True
#         return False

    def getRandomPos(self, zone):
        return random.choice(self.zonePositions[zone])

if __name__ == "__main__":
    game = Game()