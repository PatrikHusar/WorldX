from dataSaving import DataSaving
from serverHTML.serverHTML import ServerHTML
import data
from player import Player
from serverTCP import Server
# from mapper import PygameMapper
from threading import Thread
from entity import Entity
import time
import random
from chest import Chest

class Game:
    def __init__(self):
        self.world = []
        self.zonePositions = {}
        self.entitiesPos = {}
        self.playersPos = {}
        self.chestsPos = {}
        self.idCounter = 0
        self.adressToPassword = {}
        self.worldSaver = DataSaving(data.worldFilePath)
        world = self.worldSaver.loadData()
        if world:
            self.world = world
            # self.delOldEntities()
        else:
            self.createNewWorld()
            self.worldSaver.saveData(self.world)
        self.playerSaver = DataSaving(data.playersFilePath)
        self.restorePlayers()
        self.TCPserver = Server(("0.0.0.0", 5001), self.processClientData)
        self.webServer = ServerHTML(host="0.0.0.0", port=5000, game=self)
        self.initZonePositions()
        self.spawnEntities()
        self.spawnChests()
        Thread(target=self.main, daemon=True).start()
        self.webServer.startServer()

    def spawnChests(self):
        for zone in data.entitySpawn.keys():
            for i in range(data.maxChestInZone[zone]):
                self.chestsPos[self.idCounter] = self.getRandomPos(zone)
                details = data.getObjectInfo(30)
                details['drops'].append(random.choice(data.chestDrops[zone]))
                chest = Chest(self.chestsPos[self.idCounter], details, self.idCounter, self)
                self.world[chest.y][chest.x]['entities'][self.idCounter] = chest
                self.idCounter += 1

    def createPlayer(self, password, restore=False):
        player = Player(data.spawnPos, data.getObjectInfo(27), self.idCounter, self, password)
        self.idCounter += 1
        if restore:
            player.restorePlayer(restore['chestInventory'], restore['inventory'], restore['graves'])
        self.playersPos[player.playerId] = (int(player.x), int(player.y))
        self.world[int(player.y)][int(player.x)]['entities'][player.playerId] = player
        self.savePlayer(player)

    def restorePlayers(self):
        players = self.playerSaver.loadData()
        if players == None:
            return
        for playerPassword in players:
            self.createPlayer(playerPassword, players[playerPassword])

    def savePlayer(self, player):
        saveData = {}
        saveData['chestInventory'] = player.player['chestInventory']
        saveData['inventory'] = player.player['inventory']
        saveData['graves'] = player.player['graves']
        loadData = self.playerSaver.loadData()
        if loadData == None:
            loadData = {}
        loadData[player.password] = saveData
        self.playerSaver.saveData(loadData)

    def initZonePositions(self):
        for y in range(data.worldSize):
            for x in range(data.worldSize):
                zoneName = self.world[y][x]['zone']
                if self.world[y][x]['block']['typeId'] in data.spawnableBlockIds:
                    if zoneName in self.zonePositions:
                        self.zonePositions[zoneName].append((x, y))
                    else:
                        self.zonePositions[zoneName] = [(x, y)]

    def spawnEntities(self):
        for zone in data.zones:
            zoneType = zone['zone']
            for _ in range(data.maxEnemiesInZone[zoneType]):
                self.entitiesPos[self.idCounter] = self.getRandomPos(zoneType)
                entity = Entity(self.entitiesPos[self.idCounter], data.getObjectInfo(data.entitySpawn[zoneType]), self.idCounter, self)
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
    def getChestsList(self):
        chests = []
        for id in self.chestsPos.keys():
            chests.append(self.world[self.chestsPos[id][1]][self.chestsPos[id][0]]['entities'][id])
        return chests
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
            elif entityObj.__class__.__name__ == 'Player':
                self.playersPos[id] = (newX, newY)
            elif entityObj.__class__.__name__ == 'Chest':
                self.chestsPos[id] = (newX, newY)
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
        return None
    def processClientData(self, playerMessage, adress):
        if playerMessage.startswith('login:'):
            if adress in self.adressToPassword:
                return 'login failed, only 1 account on computer is allowed'
            password = playerMessage[6:]
            if self.getPlayerByPassword(password) == None:
                self.createPlayer(password)
            self.adressToPassword[adress] = password
            return 'logged in to the server, have fun!'
        elif playerMessage == 'disconnect':
            try:
                del self.adressToPassword[adress]
            except:
                # already disconnected
                pass
        elif adress in self.adressToPassword:
            if playerMessage.startswith(tuple(['forward', 'left', 'right', 'turnTo:', 'interact:', 'attack'])):
                self.getPlayerByPassword(self.adressToPassword[adress]).actions.append(playerMessage)
            else:
                if playerMessage.startswith('getPos'):
                    player = self.getPlayerByPassword(self.adressToPassword[adress])
                    return (player.x, player.y)
        return None
#     def changeBlock(self, x, y, newId):
#         if self.checkIfInsideWorld(x, y, 0, 0):
#             self.world[y][x] = data.getObjectInfo(newId)
#             self.saver.saveWorld(self.world)
#             return True
#         return False

    def getRandomPos(self, zone):
        """returns (x, y)"""
        return random.choice(self.zonePositions[zone])

if __name__ == "__main__":
    game = Game()