import data
from inventory import*

class Player:
    def __init__(self, pos, player, id, game, password):
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.dir = 'north'
        self.myId = id
        self.isMoving = False
        self.eDetails = player
        self.game = game
        self.name = ''
        self.password = password
        self.offsets = {'north': (0, -1), 'east': (1, 0), 'south': (0, 1), 'west': (-1, 0)}
        self.moveTargetX = float(self.x)
        self.moveTargetY = float(self.y)
        self.lastActionTime = 0
        self.lastAttackTime = 0
        self.lastSkinUpdate = 0
        self.actions = []
        self.noMoveActions = []

    def equipItem(self, action, restoring=False):
        item = action[:action.find('|')]
        slot = action[action.find('|') + 1:]
        if slot in getEquipped(self):
            if item in getInventory(self) and slot in self.game.getValue('bodySlot', ['name', item]) and getEquipped(self, slot) == None or restoring:
                equipItemToSlot(self, item, slot)
                boosts = self.game.getValue('boosts', ['name', item])
                for boost in boosts:
                    self.eDetails[boost] += boosts[boost]

    def unequipItem(self, slot):
        if slot in getEquipped(self):
            if not getEquipped(self, slot) == None:
                item = unequipItemFromSlot(self, slot)
                boosts = self.game.getValue('boosts', ['name', item])
                for boost in boosts:
                    self.eDetails[boost] -= boosts[boost]

    def storeItem(self, item):
        if item in getInventory(self):
            storeItemToChest(self, item)
    def takeItem(self, item):
        if item in getChestInventory(self):
            takeItemFromChest(self, item)
    def addResearchPoints(self, recipeItem):
        if recipeItem in getInventory(self) and recipeItem.startswith('recipe_'):
            item = recipeItem[7:]
            delItemFromInventory(self, recipeItem)
            if item in getResearchProgress(self):
                getResearchProgress(self)[item] += data.researchValue
            else:
                getResearchProgress(self)[item] = data.researchValue
            researchMax = self.game.getValue('research', ['name', item])
            if getResearchProgress(self)[item] >= researchMax:
                getResearchProgress(self)[item] = researchMax
    def craft(self, item):
        if item in getResearchProgress(self) and getResearchProgress(self)[item] >= self.game.getValue('research', ['name', item]):
            craftRecipe = self.game.getValue('recipe', ['name', item])
            if self.ableToCraft(craftRecipe):
                for id in craftRecipe:
                    name = self.game.getValue('name', ['typeId', id])
                    for i in range(craftRecipe[id]):
                        delItemFromInventory(self, name)
                addItemToInventory(self, item, True)
    def ableToCraft(self, recipe):
        for itemId in recipe:
            if recipe[itemId] > getInventory(self).count(self.game.getValue('name', ['typeId', itemId])):
                return False
        return True
    def takeDamage(self, dmg):
        setHealth(self, getHealth(self) - dmg)
        if getHealth(self) <= 0.0:
            if len(getInventory(self)) > 0:
                items = getInventory(self)
                for item in getEquipped(self).values():
                    if item:
                        items.append(item)
                self.game.createGrave(items, (self.moveTargetX, self.moveTargetY))
            self.eDetails = self.game.getObjectInfo(getTypeId(self))
            newPos = data.spawnPos
            self.game.updateEntityMovement((self.moveTargetX, self.moveTargetY), newPos, self.myId)
            self.isMoving = False
            self.x = newPos[0]
            self.y = newPos[1]

    def attack(self, currentTime):
        if currentTime - self.lastAttackTime < getAttackPause(self):
            return
        self.lastAttackTime = currentTime
        entities = list(self.game.world[int(self.y) + self.offsets[self.dir][1]][int(self.x) + self.offsets[self.dir][0]]['entities'].values())
        if entities:
            for entity in entities:
                if not entity.__class__.__name__ == 'Chest':
                    if entity.__class__.__name__ == 'Enemy' or not self.game.world[int(self.y)][int(self.x)]['zone'] in data.noPVPzones:
                        itemIds = entity.takeDamage(getDamage(self))
                        if itemIds:
                            for id in itemIds:
                                addItemToInventory(self, self.game.getValue('name', ['typeId', id]))

    def interact(self, action):
        block = self.game.world[int(self.y) + self.offsets[self.dir][1]][int(self.x) + self.offsets[self.dir][0]]['block']
        if getBlockTypeId(block) == 10:
            if action.startswith('put:'):
                self.storeItem(action[4:])
            elif action.startswith('take:'):
                self.takeItem(action[5:])
        elif getBlockTypeId(block) == 12:
            if action.startswith('put:'):
                self.addResearchPoints(action[4:])
        elif getBlockTypeId(block) == 11:
            if action.startswith('craft:'):
                self.craft(action[6:])
        if action == 'open':
            for entity in list(self.game.world[int(self.y) + self.offsets[self.dir][1]][int(self.x) + self.offsets[self.dir][0]]['entities'].values()):
                if entity.__class__.__name__ == 'Chest':
                    self.loadInventoryWithItems(entity.openChest())
                elif entity.__class__.__name__ == 'Grave':
                    for item in self.game.claimGrave(entity.myId):
                        addItemToInventory(self, item, ignoreSpace=True)

    def showInteract(self):
        block = self.game.world[int(self.moveTargetY) + self.offsets[self.dir][1]][int(self.moveTargetX) + self.offsets[self.dir][0]]['block']
        if getBlockTypeId(block) == 12:
            recipeDict = {}
            for item in getResearchProgress(self):
                if self.game.getValue('research', ['name', item]) != 0:
                    recipeDict[item] = getResearchProgress(self)[item] / self.game.getValue('research', ['name', item])
                else:
                    recipeDict[item] = 1.0
            return recipeDict
        elif getBlockTypeId(block) == 11:
            recipes = []
            for r in getResearchProgress(self):
                if self.game.getValue('research', ['name', r]) == getResearchProgress(self)[r] or self.game.getValue('research', ['name', r]) == 0:
                    recipe = self.game.getValue('recipe', ['name', r])
                    changedRecipe = {}
                    for id in recipe:
                        changedRecipe[self.game.getValue('name', ['typeId', id])] = recipe[id]
                    recipes.append({r: changedRecipe})
            return recipes
        elif getBlockTypeId(block) == 10:
            return getChestInventory(self)
    def getData(self, message):
        if message == 'getPos':
            return (self.x, self.y)
        elif message == 'interact:show':
            return self.showInteract()

    def loadInventoryWithItems(self, ids, haveInvLimits=True):
        for id in ids:
            itemName = self.game.getValue('name', ['typeId', id])
            if itemName:
                addItemToInventory(self, itemName, haveInvLimits)

    def restorePlayer(self, restore):
        restorePlayerData(self, restore)
        
    def turnTowards(self, dir):
        self.dir = dir

    def canWalkOn(self, object):
        noEntities = True
        for entity in object['entities'].values():
            if not entity.__class__.__name__ == 'Player':
                noEntities = False
                break
        if getBlockTypeId(object['block']) in getAllowedBlocks(self) and noEntities == True:
            if not getBlockSwimmable(object['block']) == False:
                if getSwimmingSkill(self) >= getBlockSwimmable(object['block']):
                    return True
            else:
                return True
        return False

    def forward(self):        
        targetTileX = int(self.x + self.offsets[self.dir][0])
        targetTileY = int(self.y + self.offsets[self.dir][1])
        if self.game.checkIfInsideWorld(targetTileX, targetTileY, 1, 1):
            if self.canWalkOn(self.game.world[targetTileY][targetTileX]):
                self.executeStep()

    def turnLeft(self):
        self.dir = data.dirs[data.dirs.index(self.dir) - 1]

    def turnRight(self):
        self.dir = data.dirs[(data.dirs.index(self.dir) + 1) % 4]
    
    def updatePhysics(self, deltaTime, currentTime):
        if not self.isMoving:
            return
        step = getSpeed(self) * deltaTime
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
            self.lastActionTime = currentTime

    def executeStep(self):
        oldX, oldY = int(self.x), int(self.y)
        newX = oldX + self.offsets[self.dir][0]
        newY = oldY + self.offsets[self.dir][1]
        self.moveTargetX = float(newX)
        self.moveTargetY = float(newY)
        self.isMoving = True
        self.game.updateEntityMovement((oldX, oldY), (newX, newY), self.myId)

    def doAction(self, currentTime):
        if currentTime - self.lastActionTime < getWalkPause(self):
            return
        self.noMoveAction(currentTime)
        if not self.isMoving:
            self.moveAction(currentTime)
    
    def setSkinT(self, transparency):
        self.lastSkinUpdate += 0.1
        self.game.setSkinTransparency(self.name, transparency)

    def noMoveAction(self, currentTime):
        if self.noMoveActions:
            act = self.noMoveActions.pop(0)
            if act.startswith('setSkin:'):
                if currentTime - self.lastSkinUpdate > getSkinUpdatePause(self):
                    self.lastSkinUpdate = currentTime
                    self.game.setSkin(self.name, act[8:])
            elif act.startswith('equip:'):
                self.equipItem(act[6:])
                self.game.savePlayer(self)
                self.lastActionTime = currentTime
            elif act.startswith('unequip:'):
                self.unequipItem(act[8:])
                self.game.savePlayer(self)
                self.lastActionTime = currentTime

    def moveAction(self, currentTime):
        if self.actions:
            act = self.actions.pop(0)
            if act == 'forward':
                self.forward()
            elif act == 'left':
                self.turnLeft()
            elif act == 'right':
                self.turnRight()
            elif act.startswith('turnTo:'):
                self.turnTowards(act[6:])
            elif act.startswith('interact:'):
                self.interact(act[9:])
                self.game.savePlayer(self)
            elif act == 'attack':
                self.attack(currentTime)
                self.game.savePlayer(self)

            self.lastActionTime = currentTime