import data

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
        self.actions = []

    def equipItem(self, item, slot):
        if slot in self.eDetails['equipped'] and item in self.eDetails['inventory'] and slot in item['bodySlot'] and self.eDetails['equipped'][slot] == None:
            self.eDetails['inventory'].remove(item)
            self.eDetails['inventorySpace'] += 1
            self.eDetails['equipped'][slot] = item
            boosts = self.game.getValue('boosts', ['name', item])
            for boost in boosts:
                self.eDetails[boost] += boosts[boost]

    def unequipItem(self, slot):
        if slot in self.eDetails['equipped']:
            item = self.eDetails['equipped'][slot]
            self.eDetails['equipped'][slot] = None
            self.eDetails['inventory'].append(item)
            self.eDetails['inventorySpace'] -= 1
            boosts = self.game.getValue('boosts', ['name', item])
            for boost in boosts:
                self.eDetails[boost] -= boosts[boost]

    def storeItem(self, item):
        if item in self.eDetails['inventory']:
            self.eDetails['inventory'].remove(item)
            self.eDetails['inventorySpace'] += 1
            self.eDetails['chestInventory'].append(item)
    def takeItem(self, item):
        if item in self.eDetails['chestInventory']:
            self.eDetails['chestInventory'].remove(item)
            self.eDetails['inventory'].append(item)
            self.eDetails['inventorySpace'] -= 1
    def addResearchPoints(self, recipeItem):
        if recipeItem in self.eDetails['inventory'] and recipeItem.startswith('recipe_'):
            item = recipeItem[7:]
            self.eDetails['inventory'].remove(recipeItem)
            self.eDetails['inventorySpace'] += 1
            if item in self.eDetails['researchProgress']:
                self.eDetails['researchProgress'][item] += data.researchValue
            else:
                self.eDetails['researchProgress'][item] = data.researchValue
            researchMax = self.game.getValue('research', ['name', item])
            if self.eDetails['researchProgress'][item] >= researchMax:
                self.eDetails['researchProgress'][item] = researchMax
    def craft(self, item):
        if item in self.eDetails['researchProgress'] and self.eDetails['researchProgress'][item] == self.game.getValue('research', ['name', item]):
            craftRecipe = self.game.getValue('recipe', ['name', item])
            if self.ableToCraft(craftRecipe):
                for id in craftRecipe:
                    name = self.game.getValue('name', ['typeId', id])
                    for i in range(craftRecipe[id]):
                        self.eDetails['inventory'].remove(name)
                        self.eDetails['inventorySpace'] += 1
                self.eDetails['inventory'].append(item)
                self.eDetails['inventorySpace'] -= 1
    def ableToCraft(self, recipe):
        for itemId in recipe:
            if recipe[itemId] > self.eDetails['inventory'].count(self.game.getValue('name', ['typeId', itemId])):
                return False
        return True
    def takeDamage(self, dmg):
        self.eDetails['health'] -= dmg
        if self.eDetails['health'] <= 0.0:
            if len(self.eDetails['inventory']) > 0:
                items = self.eDetails['inventory']
                for item in self.eDetails['equipped'].values():
                    if item:
                        items.append(item)
                self.game.createGrave(items, (self.moveTargetX, self.moveTargetY))
            self.eDetails = self.game.getObjectInfo(self.eDetails['typeId'])
            newPos = data.spawnPos
            self.game.updateEntityMovement((self.moveTargetX, self.moveTargetY), newPos, self.myId)
            self.isMoving = False
            self.x = newPos[0]
            self.y = newPos[1]

    def attack(self, currentTime):
        if currentTime - self.lastAttackTime < self.eDetails['attackPause']:
            return
        self.lastAttackTime = currentTime
        entities = list(self.game.world[int(self.y) + self.offsets[self.dir][1]][int(self.x) + self.offsets[self.dir][0]]['entities'].values())
        if entities:
            for entity in entities:
                if not entity.__class__.__name__ == 'Chest':
                    if entity.__class__.__name__ == 'Entity' or not self.game.world[int(self.y)][int(self.x)]['zone'] in data.noPVPzones:
                        itemIds = entity.takeDamage(self.eDetails['damage'])
                        if itemIds:
                            for id in itemIds:
                                if self.eDetails['inventorySpace'] >= 1:
                                    self.eDetails['inventorySpace'] -= 1
                                    self.eDetails['inventory'].append(self.game.getValue('name', ['typeId', id]))

    def interact(self, action):
        block = self.game.world[int(self.y) + self.offsets[self.dir][1]][int(self.x) + self.offsets[self.dir][0]]['block']
        if block['typeId'] == 10:
            if action.startswith('put:'):
                self.storeItem(action[4:])
            elif action.startswith('take:'):
                self.takeItem(action[5:])
        elif block['typeId'] == 12:
            if action.startswith('put:'):
                self.addResearchPoints(action[4:])
        elif block['typeId'] == 11:
            if action.startswith('craft:'):
                self.craft(action[6:])
        if action == 'open':
            for entity in list(self.game.world[int(self.y) + self.offsets[self.dir][1]][int(self.x) + self.offsets[self.dir][0]]['entities'].values()):
                if entity.__class__.__name__ == 'Chest':
                    self.loadInventoryWithItems(entity.openChest())
                elif entity.__class__.__name__ == 'Grave':
                    for item in self.game.claimGrave(entity.myId):
                        self.eDetails['inventory'].append(item)

    def showInteract(self):
        block = self.game.world[int(self.y) + self.offsets[self.dir][1]][int(self.x) + self.offsets[self.dir][0]]['block']
        if block['typeId'] == 12:
            return self.eDetails['researchProgress']
        elif block['typeId'] == 11:
            recipes = []
            for r in self.eDetails['researchProgress']:
                if self.game.getValue('research', ['name', r]) == self.eDetails['researchProgress'][r]:
                    recipe = self.game.getValue('recipe', ['name', r])
                    changedRecipe = {}
                    for id in recipe:
                        changedRecipe[self.game.getValue('name', ['typeId', id])] = recipe[id]
                    recipes.append({r: changedRecipe})
            return recipes
        elif block['typeId'] == 10:
            return self.eDetails['chestInventory']

    def loadInventoryWithItems(self, ids, haveInvLimits=True):
        for id in ids:
            itemName = self.game.getValue('name', ['typeId', id])
            if itemName:
                if self.eDetails['inventorySpace'] >= 1 or haveInvLimits == False:
                    self.eDetails['inventorySpace'] -= 1
                    self.eDetails['inventory'].append(itemName)

    def restorePlayer(self, chestInventory, inventory, name, research):
        self.eDetails['chestInventory'] = chestInventory
        self.eDetails['inventory'] = inventory
        self.eDetails['researchProgress'] = research
        self.name = name

    def turnTowards(self, currentTime, dir):
        if currentTime - self.lastActionTime < self.eDetails['walkPause'] or self.isMoving:
            return
        self.lastActionTime = currentTime
        self.dir = dir

    def canWalkOn(self, object):
        noEntities = True
        for entity in object['entities'].values():
            if not entity.__class__.__name__ == 'Player':
                noEntities = False
                break
        if object['block']['typeId'] in self.eDetails['allowedBlocks'] and noEntities == True:
            if not object['block']['swimmable'] == False:
                if self.eDetails['swimmingSkill'] >= object['block']['swimmable']:
                    return True
            else:
                return True
                
        return False

    def forward(self, currentTime):
        if currentTime - self.lastActionTime < self.eDetails['walkPause'] or self.isMoving:
            return
        self.lastActionTime = currentTime
        
        targetTileX = int(self.x + self.offsets[self.dir][0])
        targetTileY = int(self.y + self.offsets[self.dir][1])
        
        if self.game.checkIfInsideWorld(targetTileX, targetTileY, 1, 1):
            if self.canWalkOn(self.game.world[targetTileY][targetTileX]):
                self.executeStep()

    def turnLeft(self, currentTime):
        if currentTime - self.lastActionTime < self.eDetails['walkPause'] or self.isMoving:
            return
        self.lastActionTime = currentTime
        self.dir = data.dirs[data.dirs.index(self.dir) - 1]

    def turnRight(self, currentTime):
        if currentTime - self.lastActionTime < self.eDetails['walkPause'] or self.isMoving:
            return
        self.lastActionTime = currentTime
        self.dir = data.dirs[(data.dirs.index(self.dir) + 1) % 4]
    
    def updatePhysics(self, deltaTime, currentTime):
        if not self.isMoving:
            return
        step = self.eDetails['speed'] * deltaTime

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
        if currentTime - self.lastActionTime < self.eDetails['walkPause'] or self.isMoving:
            return
        if self.actions:
            act = self.actions.pop(0)
            if act == 'forward':
                self.forward(currentTime)
            elif act == 'left':
                self.turnLeft(currentTime)
            elif act == 'right':
                self.turnRight(currentTime)
            elif act.startswith('turnTo:'):
                self.turnTowards(currentTime, act[6:])
            elif act.startswith('interact:'):
                if act == 'interact:':
                    self.interact()
                else:
                    self.interact(act[9:])
            elif act.startswith('attack'):
                self.attack(currentTime)