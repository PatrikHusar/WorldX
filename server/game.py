from dataSaving import DataSaving
from serverHTML.serverHTML import ServerHTML
import data
from player import Player
from serverTCP import Server
# from mapper import PygameMapper
from threading import Thread
from enemy import Enemy
import time
import random
from chest import Chest
from grave import Grave
import copy
from skinMaker import SkinMaker
import inventory

class Game:
    def __init__(self):
        self.world = []
        self.zonePositions = {}
        self.entitiesPos = {}
        self.idCounter = 0
        self.adressToPassword = {}
        self.worldSaver = DataSaving(data.worldFilePath)
        self.skinMake = SkinMaker(data.imagesFilePath)
        world = self.worldSaver.loadData()
        if world:
            self.world = world
            # self.delOldEntities()
        else:
            self.createNewWorld()
            self.worldSaver.saveData(self.world)
        self.playerSaver = DataSaving(data.playersDataFilePath)
        self.restorePlayers()
        self.TCPserver = Server(("0.0.0.0", 5001), self.processClientData)
        self.webServer = ServerHTML(host="0.0.0.0", port=5000, game=self)
        self.initZonePositions()
        self.spawnEnemies()
        self.spawnChests()
        Thread(target=self.main, daemon=True).start()
        self.webServer.startServer()

    def spawnChests(self):
        for zone in data.entitySpawn.keys():
            for i in range(data.maxChestInZone[zone]):
                self.entitiesPos[self.idCounter] = self.getRandomPos(zone)
                details = self.getObjectInfo(30)
                details['drops'].append(random.choice(data.chestDrops[zone]))
                chest = Chest(self.entitiesPos[self.idCounter], details, self.idCounter, self)
                self.world[chest.y][chest.x]['entities'][self.idCounter] = chest
                self.idCounter += 1

    def createPlayer(self, password, restore=False):
        player = Player(data.spawnPos, self.getObjectInfo(27), self.idCounter, self, password)
        self.idCounter += 1
        if restore:
            player.restorePlayer(restore)
        else:
            names = self.getPlayerNames()
            for _ in range(100):
                name = self.generatePlayerName(names)
                if name:
                    player.name = name
                    break
            self.skinMake.createSkin(player.name, '')
        self.entitiesPos[player.myId] = (int(player.x), int(player.y))
        self.world[int(player.y)][int(player.x)]['entities'][player.myId] = player
        self.savePlayer(player)

    def restorePlayers(self):
        players = self.playerSaver.loadData()
        if players == None:
            return
        for playerPassword in players:
            self.createPlayer(playerPassword, players[playerPassword])
    
    def getPlayerNames(self):
        names = []
        for player in self.getEntitiesList('player'):
            names.append(player.name)
        return names

    def savePlayer(self, player):
        loadData = self.playerSaver.loadData()
        if loadData == None:
            loadData = {}
        loadData[player.password] = inventory.savePlayerData(player)
        self.playerSaver.saveData(loadData)

    def initZonePositions(self):
        for y in range(data.worldSize):
            for x in range(data.worldSize):
                zoneName = self.world[y][x]['zone']
                if inventory.getBlockTypeId(self.world[y][x]['block']) in data.spawnableBlockIds:
                    if zoneName in self.zonePositions:
                        self.zonePositions[zoneName].append((x, y))
                    else:
                        self.zonePositions[zoneName] = [(x, y)]

    def spawnEnemies(self):
        for zone in data.zones:
            zoneType = zone['zone']
            for _ in range(data.maxEnemiesInZone[zoneType]):
                self.entitiesPos[self.idCounter] = self.getRandomPos(zoneType)
                enemy = Enemy(self.entitiesPos[self.idCounter], self.getObjectInfo(data.entitySpawn[zoneType]), self.idCounter, self)
                self.world[int(enemy.y)][int(enemy.x)]['entities'][enemy.myId] = enemy
                self.idCounter += 1
    
    def createGrave(self, inventory, pos):
        grave = Grave(pos, self.getObjectInfo(25), self.idCounter, inventory)
        self.idCounter += 1
        self.world[int(grave.y)][int(grave.x)]['entities'][grave.myId] = grave
        self.entitiesPos[grave.myId] = (int(grave.x), int(grave.y))
    def claimGrave(self, graveId):
        pos = self.entitiesPos[graveId]
        grave = self.world[pos[1]][pos[0]]['entities'][graveId]
        items = grave.claimGrave()
        del self.world[pos[1]][pos[0]]['entities'][graveId]
        del self.entitiesPos[graveId]
        return items

    def main(self):
        deltaTime = 0.01
        enemies = self.getEntitiesList('enemy')
        lastUpdate = 0
        updateInterval = 0.05
        while True:
            currentTime = time.perf_counter()
            for ent in enemies:
                ent.move(currentTime=currentTime)
                ent.updatePhysics(deltaTime, currentTime)
            players = self.getEntitiesList('player')
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
                for ent in object['entities']:
                    if ent.__class__.__name__ != 'Grave':
                        del ent
    def getEntitiesList(self, eType=None):
        entities = []
        for id in self.entitiesPos.keys():
            if self.world[self.entitiesPos[id][1]][self.entitiesPos[id][0]]['entities'][id].eDetails['type'] == eType or eType == None:
                entities.append(self.world[self.entitiesPos[id][1]][self.entitiesPos[id][0]]['entities'][id])
        return entities
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
            self.entitiesPos[id] = (newX, newY)

    def createNewWorld(self):
        self.world = []
        for r in range(data.worldSize):
            row = []
            for c in range(data.worldSize):
                object = data.zones[0]
                object['block'] = self.getObjectInfo(object['block'])
                row.append(object)
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
        for player in self.getEntitiesList('player'):
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
                pass # already disconnected
        elif adress in self.adressToPassword:
            if playerMessage == 'getPos':
                return self.getPlayerByPassword(self.adressToPassword[adress]).getData(playerMessage)
            elif playerMessage == 'interact:show':
                return self.getPlayerByPassword(self.adressToPassword[adress]).getData(playerMessage)
            elif playerMessage.startswith(tuple(['setSkin:', 'equip:', 'unequip:'])):
                self.getPlayerByPassword(self.adressToPassword[adress]).noMoveActions.append(playerMessage)
            elif playerMessage.startswith(tuple(['forward', 'left', 'right', 'turnTo:', 'interact:', 'attack'])):
                self.getPlayerByPassword(self.adressToPassword[adress]).actions.append(playerMessage)
                
        return None
#     def changeBlock(self, x, y, newId):
#         if self.checkIfInsideWorld(x, y, 0, 0):
#             self.world[y][x] = self.getObjectInfo(newId)
#             self.saver.saveWorld(self.world)
#             return True
#         return False

    def getRandomPos(self, zone):
        """returns (x, y)"""
        return random.choice(self.zonePositions[zone])

    def getValue(self, x, y):
        """returns value from key {x} in item that has in key {a} value {b}. y = [a, b]"""
        return next((item[x] for item in data.items if item[y[0]] == y[1]), None)
    def getObjectInfo(self, id):
        for object in data.objects:
            if object['typeId'] == id:
                return copy.deepcopy(object)
        return None
    def getObjectList(self, type):
        objectList = []
        for object in data.objects:
            if object['type'] == type:
                objectList.append(object)
        return objectList
    def generatePlayerName(self, alreadyCreatedNames):
        name = f"{random.choice(data.PREFIXES)}{random.choice(data.SUFFIXES)}{random.randint(10, 99)}"
        if name not in alreadyCreatedNames:
            return name
        return None
    def setSkin(self, name, skin):
        self.skinMake.createSkin(name, skin)

if __name__ == "__main__":
    game = Game()