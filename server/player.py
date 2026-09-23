import data
from inventory import*

class Player:
    def __init__(self, pos, player, id, game, password):
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.oldX, self.oldY = self.x, self.y
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
        self.changedPos = False
        self.lastMoveTime = 0
        self.lastInteractionTime = 0
        self.lastAttackTime = 0
        self.lastSkinUpdate = 0
        self.lastGetDataTime = 0
        self.lastRegenTime = 0
        self.actions = []
        self.actionRules = [
            {
                'timeAttr': 'lastMoveTime',
                'pauseFn': getWalkPause,
                'actions': [
                    ('forward', lambda _: self.forward(), False),
                    ('left', lambda _: self.turnLeft(), False),
                    ('right', lambda _: self.turnRight(), False),
                    ('turnTo:', lambda arg: self.turnTowards(arg), False),
                    ('equip:', lambda arg: self.equipItem(arg), True),
                    ('unequip:', lambda arg: self.unequipItem(arg), True),]
            },{
                'timeAttr': 'lastInteractionTime',
                'pauseFn': getInteractionPause,
                'actions': [
                    ('interact:', lambda arg: self.interact(arg), True),]
            },{
                'timeAttr': 'lastAttackTime',
                'pauseFn': getAttackPause,
                'actions': [
                    ('attack', lambda _: self.attack(), True),]
            },{
                'timeAttr': 'lastSkinUpdate',
                'pauseFn': getSkinUpdatePause,
                'actions': [
                    ('setSkin:', lambda arg: self.game.setSkin(self.name, arg), False)]
            }]

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
            if self.changedPos == True:
                oldPos = (int(self.moveTargetX), int(self.moveTargetY))
            else:
                oldPos = (int(self.oldX), int(self.oldY))
            self.changedPos = False
            if len(getInventory(self)) > 0:
                items = getInventory(self)
                for item in getEquipped(self).values():
                    if item:
                        items.append(item)
                self.game.createGrave(items, oldPos)
                self.actions = []
            self.eDetails = self.game.getObjectInfo(getTypeId(self))
            newPos = data.spawnPos
            self.game.updateEntityMovement(oldPos, newPos, self.myId)
            self.isMoving = False
            self.x = newPos[0]
            self.y = newPos[1]
            self.oldX, self.oldY = self.x, self.y

    def attack(self):
        for i in range(getReach(self)):
            entities = list(self.game.world[int(self.y) + self.offsets[self.dir][1] * (i + 1)][int(self.x) + self.offsets[self.dir][0] * (i + 1)]['entities'].values())
            if entities:
                for entity in entities:
                    if not entity.__class__.__name__ in ['Chest', 'Grave']:
                        if entity.__class__.__name__ == 'Enemy' or not self.game.world[int(self.y)][int(self.x)]['zone'] in data.noPVPzones:
                            itemIds = entity.takeDamage(getDamage(self))
                            if itemIds:
                                for id in itemIds:
                                    addItemToInventory(self, self.game.getValue('name', ['typeId', id]))

    def interact(self, action):
        for i in range(getReach(self)):
            block = self.game.world[int(self.y) + self.offsets[self.dir][1] * (i + 1)][int(self.x) + self.offsets[self.dir][0] * (i + 1)]['block']
            if getBlockTypeId(block) == 10:
                if action.startswith('put:'):
                    self.storeItem(action[4:])
                elif action.startswith('take:'):
                    self.takeItem(action[5:])
                return
            elif getBlockTypeId(block) == 12:
                if action.startswith('put:'):
                    self.addResearchPoints(action[4:])
                return
            elif getBlockTypeId(block) == 11:
                if action.startswith('craft:'):
                    self.craft(action[6:])
                return
        if action == 'open':
            for i in range(getReach(self)):
                entities = self.game.world[int(self.y) + self.offsets[self.dir][1] * (i + 1)][int(self.x) + self.offsets[self.dir][0] * (i + 1)]['entities'].values()
                for entity in list(entities):
                    if entity.__class__.__name__ == 'Chest':
                        self.loadInventoryWithItems(entity.openChest())
                        return
                    elif entity.__class__.__name__ == 'Grave':
                        for item in self.game.claimGrave(entity.myId):
                            addItemToInventory(self, item, ignoreSpace=True)
                        return
    def showInteract(self):
        for i in range(getReach(self)):
            block = self.game.world[int(self.y) + self.offsets[self.dir][1] * (i + 1)][int(self.x) + self.offsets[self.dir][0] * (i + 1)]['block']
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
    def getData(self, message, currentTime):
        if currentTime - self.lastGetDataTime > getGetDataTimeout(self):
            self.lastGetDataTime = currentTime
            if message == 'getPos':
                return (self.x, self.y)
            elif message == 'interact:show':
                return self.showInteract()
            elif message == 'getMap':
                map = self.game.getMapPart(int(self.x) - getSight(self), int(self.y) - getSight(self), getSight(self) * 2 + 1, getSight(self) * 2 + 1)
                return self.game.transformMapForClient(map)
            elif message == 'resetActions':
                self.actions = []

    def loadInventoryWithItems(self, ids, haveInvLimits=True):
        for id in ids:
            itemName = self.game.getValue('name', ['typeId', id])
            if itemName:
                addItemToInventory(self, itemName, haveInvLimits)

    def restorePlayer(self, restore):
        restorePlayerData(self, restore)

    def canWalkOn(self, object, checkEntities=True):
        noEntities = True
        for entity in object['entities'].values():
            if not entity.__class__.__name__ == 'Player':
                noEntities = False
                break
        if getBlockTypeId(object['block']) in getAllowedBlocks(self) and (noEntities == True or checkEntities == False):
            if not getBlockSwimmable(object['block']) == False:
                if getSwimmingSkill(self) >= getBlockSwimmable(object['block']):
                    return True
            else:
                return True
        return False

    def turnTowards(self, dir):
        self.dir = dir

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
        if (abs(self.moveTargetX - self.x) < 0.5 and self.x != self.moveTargetX) or (abs(self.moveTargetY - self.y) < 0.5 and self.y != self.moveTargetY):
            self.changedPos = True
            self.game.updateEntityMovement((self.moveTargetX - self.offsets[self.dir][0], self.moveTargetY - self.offsets[self.dir][1]), (self.moveTargetX, self.moveTargetY), self.myId)
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
            self.lastMoveTime = currentTime
            self.oldX, self.oldY = self.x, self.y

    def executeStep(self):
        self.oldX, self.oldY = int(self.x), int(self.y)
        newX = self.oldX + self.offsets[self.dir][0]
        newY = self.oldY + self.offsets[self.dir][1]
        self.moveTargetX = float(newX)
        self.moveTargetY = float(newY)
        self.isMoving = True
        self.changedPos = False

    def defaultControl(self, currentTime):
        if currentTime - self.lastRegenTime > 2:
            self.lastRegenTime = currentTime
            setHealth(self, getHealth(self) + getRegeneration(self))
            if getHealth(self) > getMaxHealth(self):
                setHealth(self, getMaxHealth(self))
            if self.canWalkOn(self.game.world[int(self.y)][int(self.x)], False) == False:
                setHealth(self, getHealth(self) - getRegeneration(self) - 8)

    def doAction(self, currentTime):
        self.defaultControl(currentTime)
        if self.isMoving or not self.actions:
            return
        act = self.actions[0]
        for category in self.actionRules:
            attrName = category['timeAttr']
            if currentTime - getattr(self, attrName) > category['pauseFn'](self):
                for action, handler, shouldSave in category['actions']:
                    if act.startswith(action):
                        arg = act[len(action):]
                        handler(arg)
                        setattr(self, attrName, currentTime)
                        self.actions.pop(0)
                        if shouldSave:
                            self.game.savePlayer(self)
                        return

    def setSkinT(self, transparency):
        self.game.setSkinTransparency(self.name, transparency)
        self.lastSkinUpdate += 5
