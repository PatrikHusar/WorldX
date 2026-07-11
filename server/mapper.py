import pygame
import sys
import os
from PIL import Image as PILImage

"""pygame world editor"""
class PygameMapper:
    def __init__(self, getMapPart, blockChange, worldSize, blockList, idToName):
        pygame.init()
        
        self.screenWidth = 1600
        self.screenHeight = 800
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        pygame.display.set_caption("WorldX Editor")
        
        self.getMapPart = getMapPart
        self.blockChange = blockChange
        self.worldSize = worldSize
        self.idToName = idToName
        
        self.blockList = [obj for obj in blockList if obj['type'] == 'block']
        self.selectedBlockId = self.blockList[0]['id'] if self.blockList else 0
        
        self.cameraX = 75.0
        self.cameraY = 60.0
        self.baseBlockSize = 40
        self.currentBlockSize = 40
        self.clampCamera()
        
        self.isDrawing = False
        self.isPanning = False
        self.sidebarScrollY = 0  
        
        self.entities = []
        self.selectedEntity = None
        self.clock = pygame.time.Clock()
        
        staticDir = os.path.join(os.path.dirname(__file__), 'serverHTML', 'static')
        
        self.textures = {}
        for block in self.blockList:
            blockId = block['id']
            blockName = idToName.get(blockId, f"unknown_{blockId}")
            imgPath = os.path.join(staticDir, f"{blockName}.png")
            self.textures[blockId] = self._loadTexture(imgPath, (120, 50, 50))

        self.entityTextures = {}
        for eId, eName in idToName.items():
            self.entityTextures[eId] = {}
            for direction in ['north', 'east', 'south', 'west']:
                imgName = f"{eName}{direction}.png"
                imgPath = os.path.join(staticDir, imgName)
                
                self.entityTextures[eId][direction] = self._loadTexture(imgPath, (255, 235, 59), fallbackSize=(32, 32))

        self.clock = pygame.time.Clock()

    def _loadTexture(self, imgPath, fallbackColor, fallbackSize=(32, 32)):
        if os.path.exists(imgPath):
            try:
                pilImg = PILImage.open(imgPath).convert("RGBA")
                pygameSurface = pygame.image.fromstring(pilImg.tobytes(), pilImg.size, "RGBA")
                return pygameSurface.convert_alpha()
            except Exception as e:
                print(f"error pillow loading {imgPath}: {e}")
        surface = pygame.Surface(fallbackSize)
        surface.fill(fallbackColor)
        return surface

    def updateEntities(self, newEntities):
        self.entities = newEntities

    def drawCustomText(self, text, startX, startY, color=(255, 255, 255), scale=2):
        currentX = startX
        glyphs = {
            '0': [(0,0,1,0), (1,0,1,2), (1,2,0,2), (0,2,0,0)], '1': [(1,0,1,2)],
            '2': [(0,0,1,0), (1,0,1,1), (1,1,0,1), (0,1,0,2), (0,2,1,2)],
            '3': [(0,0,1,0), (1,0,1,2), (1,1,0,1), (1,2,0,2)], '4': [(0,0,0,1), (0,1,1,1), (1,0,1,2)],
            '5': [(1,0,0,0), (0,0,0,1), (0,1,1,1), (1,1,1,2), (1,2,0,2)],
            '6': [(1,0,0,0), (0,0,0,2), (0,2,1,2), (1,2,1,1), (1,1,0,1)], '7': [(0,0,1,0), (1,0,1,2)],
            '8': [(0,0,1,0), (1,0,1,2), (0,2,1,2), (0,0,0,2), (0,1,1,1)],
            '9': [(0,1,1,1), (0,0,1,0), (1,0,1,2), (0,0,0,1), (1,2,0,2)],
            'x': [(0,0.5,1,1.5), (0,1.5,1,0.5)], 'y': [(0,0.5,0.5,1), (1,0.5,0.5,1), (0.5,1,0.5,2)],
            ':': [(0.5,0.4,0.5,0.5), (0.5,1.4,0.5,1.5)], ',': [(0.5,1.5,0.3,1.9)], ' ': []
        }
        for char in str(text).lower():
            if char in glyphs:
                for line in glyphs[char]:
                    x1, y1, x2, y2 = line
                    p1 = (int(currentX + x1 * 5 * scale), int(startY + y1 * 6 * scale))
                    p2 = (int(currentX + x2 * 5 * scale), int(startY + y2 * 6 * scale))
                    pygame.draw.line(self.screen, color, p1, p2, int(max(1, scale)))
            currentX += int(7 * scale)
            
    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            mousePos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        self.handleTeleport()
                    
                elif event.type == pygame.MOUSEWHEEL:
                    if mousePos[0] >= self.screenWidth - 120:
                        if event.y > 0:
                            self.sidebarScrollY = min(0, self.sidebarScrollY + 30)
                        else:
                            maxScroll = -max(0, (len(self.blockList) * 65 + 60) - self.screenHeight)
                            self.sidebarScrollY = max(maxScroll, self.sidebarScrollY - 30)
                    else:
                        direction = 1 if event.y > 0 else -1
                        self.handleZoom(direction, mousePos)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  
                        if mousePos[0] < self.screenWidth - 120:
                            clickedEntity = self.checkEntityClick(mousePos)
                            if clickedEntity:
                                self.selectedEntity = clickedEntity
                                self.isDrawing = False
                            else:
                                self.selectedEntity = None
                                keys = pygame.key.get_pressed()
                                if keys[pygame.K_LSHIFT]:
                                    self.floodFillAtMouse(mousePos)
                                else:
                                    self.isDrawing = True
                                    self.drawBlockAtMouse(mousePos)
                        else:
                            self.checkSidebarClick(mousePos)

                    elif event.button == 3:  
                        self.isPanning = True
                        pygame.mouse.get_rel() 
                        
                    elif event.button == 4:  
                        if mousePos[0] >= self.screenWidth - 120:
                            self.sidebarScrollY = min(0, self.sidebarScrollY + 30)
                        else:
                            self.handleZoom(1, mousePos)
                        
                    elif event.button == 5:  
                        if mousePos[0] >= self.screenWidth - 120:
                            maxScroll = -max(0, (len(self.blockList) * 65 + 60) - self.screenHeight)
                            self.sidebarScrollY = max(maxScroll, self.sidebarScrollY - 30)
                        else:
                            self.handleZoom(-1, mousePos)
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.isDrawing = False
                    elif event.button == 3:
                        self.isPanning = False
                        
                elif event.type == pygame.MOUSEMOTION:
                    if self.isDrawing and mousePos[0] < self.screenWidth - 120:
                        self.drawBlockAtMouse(mousePos)
                    elif self.isPanning:
                        relX, relY = pygame.mouse.get_rel()
                        self.cameraX -= relX / self.currentBlockSize
                        self.cameraY -= relY / self.currentBlockSize
                        self.clampCamera()

            mapAreaWidth = self.screenWidth - 120
            colsToLoad = int(mapAreaWidth / self.currentBlockSize) + 2
            rowsToLoad = int(self.screenHeight / self.currentBlockSize) + 2
            
            currentMapView = self.getMapPart(int(self.cameraX), int(self.cameraY), colsToLoad, rowsToLoad)
            self.screen.fill((34, 34, 34)) 
            
            offsetX = int((self.cameraX - int(self.cameraX)) * self.currentBlockSize)
            offsetY = int((self.cameraY - int(self.cameraY)) * self.currentBlockSize)
            
            for rIdx, row in enumerate(currentMapView):
                for cIdx, blockId in enumerate(row):
                    xPos = cIdx * self.currentBlockSize - offsetX
                    yPos = rIdx * self.currentBlockSize - offsetY
                    
                    if xPos < mapAreaWidth and yPos < self.screenHeight:
                        texture = self.textures.get(blockId)
                        if texture:
                            scaledTexture = pygame.transform.scale(texture, (self.currentBlockSize, self.currentBlockSize))
                            self.screen.blit(scaledTexture, (xPos, yPos))

            for entity in self.entities:
                entityScreenX = int((entity.x - self.cameraX) * self.currentBlockSize)
                entityScreenY = int((entity.y - self.cameraY) * self.currentBlockSize)
                
                if 0 <= entityScreenX < mapAreaWidth and 0 <= entityScreenY < self.screenHeight:
                    eId = entity.entity['id']
                    eDir = getattr(entity, 'dir', 'north')
                    
                    idTextures = self.entityTextures.get(eId, {})
                    texture = idTextures.get(eDir)
                    
                    if texture:
                        scaledTexture = pygame.transform.scale(texture, (self.currentBlockSize, self.currentBlockSize))
                        self.screen.blit(scaledTexture, (entityScreenX, entityScreenY))

            self.renderSidebar()
            self.renderCoordinates()
            self.renderEntityStats()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handleTeleport(self):
        print("\n--- TELEPORT ---")
        try:
            vstup = input("Zadaj suradnice v formate 'x, y' (napr. 500, 300): ")
            casti = vstup.split(",")
            if len(casti) == 2:
                self.cameraX = float(casti[0].strip())
                self.cameraY = float(casti[1].strip())
                self.clampCamera()
                print(f"Teleportovany na: x={self.cameraX}, y={self.cameraY}")
        except Exception:
            print("Neplatny format suradnic!")

    def handleZoom(self, direction, mousePos):
        worldXBefore = self.cameraX + (mousePos[0] / self.currentBlockSize)
        worldYBefore = self.cameraY + (mousePos[1] / self.currentBlockSize)
        
        newSize = self.currentBlockSize + (direction * 4)
        if 10 <= newSize <= 80:
            self.currentBlockSize = newSize
            self.cameraX = worldXBefore - (mousePos[0] / self.currentBlockSize)
            self.cameraY = worldYBefore - (mousePos[1] / self.currentBlockSize)
            self.clampCamera()

    def drawBlockAtMouse(self, mousePos):
        clickC = int(self.cameraX + (mousePos[0] / self.currentBlockSize))
        clickR = int(self.cameraY + (mousePos[1] / self.currentBlockSize))
        if 0 <= clickC < self.worldSize and 0 <= clickR < self.worldSize:
            self.blockChange(clickC, clickR, self.selectedBlockId)

    def clampCamera(self):
        mapAreaWidth = self.screenWidth - 120
        maxCols = mapAreaWidth / self.currentBlockSize
        maxRows = self.screenHeight / self.currentBlockSize
        
        if self.cameraX < 0: self.cameraX = 0.0
        if self.cameraX > self.worldSize - maxCols: self.cameraX = max(0.0, self.worldSize - maxCols)
        if self.cameraY < 0: self.cameraY = 0.0
        if self.cameraY > self.worldSize - maxRows: self.cameraY = max(0.0, self.worldSize - maxRows)

    def renderSidebar(self):
        sidebarX = self.screenWidth - 120
        sidebarSurf = pygame.Surface((120, self.screenHeight))
        sidebarSurf.fill((51, 51, 51))
        
        for idx, block in enumerate(self.blockList):
            bId = block['id']
            btnY = 45 + (idx * 65) + self.sidebarScrollY
            
            if -60 <= btnY <= self.screenHeight:
                btnRect = pygame.Rect(20, btnY, 80, 55)
                borderColor = (76, 175, 80) if bId == self.selectedBlockId else (102, 102, 102)
                
                pygame.draw.rect(sidebarSurf, (68, 68, 68), btnRect)
                pygame.draw.rect(sidebarSurf, borderColor, btnRect, 2)
                
                tex = self.textures.get(bId)
                if tex:
                    scaledTex = pygame.transform.scale(tex, (32, 32))
                    sidebarSurf.blit(scaledTex, (44, btnY + 5))
        
        self.screen.blit(sidebarSurf, (sidebarX, 0))
        pygame.draw.line(self.screen, (85, 85, 85), (sidebarX, 0), (sidebarX, self.screenHeight), 4)
        pygame.draw.rect(self.screen, (51, 51, 51), (sidebarX + 2, 0, 116, 40))
        self.drawCustomText("bloky", sidebarX + 25, 12, color=(170, 170, 170), scale=1.5)
        
        for idx, block in enumerate(self.blockList):
            bId = block['id']
            bName = self.idToName.get(bId, "block")
            btnY = 45 + (idx * 65) + self.sidebarScrollY
            if 40 <= btnY <= self.screenHeight - 20:
                self.drawCustomText(bName[:6], sidebarX + 25, btnY + 40, color=(255, 255, 255), scale=1)

    def checkSidebarClick(self, mousePos):
        sidebarX = self.screenWidth - 120
        for idx, block in enumerate(self.blockList):
            btnY = 45 + (idx * 65) + self.sidebarScrollY
            btnRect = pygame.Rect(sidebarX + 20, btnY, 80, 55)
            if btnRect.collidepoint(mousePos) and btnY >= 40:
                self.selectedBlockId = block['id']
                break

    def renderCoordinates(self):
        mousePos = pygame.mouse.get_pos()
        if mousePos[0] < self.screenWidth - 120:
            clickC = int(self.cameraX + (mousePos[0] / self.currentBlockSize))
            clickR = int(self.cameraY + (mousePos[1] / self.currentBlockSize))
            
            if 0 <= clickC < self.worldSize and 0 <= clickR < self.worldSize:
                coordString = f"x:{clickC}, y:{clickR}" if 'click_c' in locals() else f"x:{clickC}, y:{clickR}"
                bgWidth = len(coordString) * 10.5 + 10
                bgRect = pygame.Rect(10, 10, bgWidth, 26)
                
                pygame.draw.rect(self.screen, (0, 0, 0), bgRect)
                self.drawCustomText(coordString, 15, 14, color=(76, 175, 80), scale=1.5)
    
    def checkEntityClick(self, mousePos):
        mapAreaWidth = self.screenWidth - 120
        
        for entity in self.entities:
            entityScreenX = int((entity.x - self.cameraX) * self.currentBlockSize)
            entityScreenY = int((entity.y - self.cameraY) * self.currentBlockSize)
            
            entityRect = pygame.Rect(entityScreenX, entityScreenY, self.currentBlockSize, self.currentBlockSize)
            
            if entityRect.collidepoint(mousePos):
                return entity
        return None

    def renderEntityStats(self):
        if not self.selectedEntity:
            return
            
        ent = self.selectedEntity
        eName = self.idToName.get(ent.entity['id'], "unknown").upper()
        
        statsLines = [
            f"--- {eName} ---",
            f"hp: {ent.health}",
            f"dmg: {ent.damage}",
            f"speed: {ent.speed}",
            f"behavior: {ent.behaviour}",
            f"dir: {ent.dir}",
            f"pos: {int(ent.x)}, {int(ent.y)}"
        ]
        
        bgHeight = len(statsLines) * 20 + 15
        bgRect = pygame.Rect(10, 45, 200, bgHeight)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bgRect)
        pygame.draw.rect(self.screen, (76, 175, 80), bgRect, 1)
        
        startY = 55
        for line in statsLines:
            self.drawCustomText(line, 20, startY, color=(255, 255, 255), scale=1.2)
            startY += 20

    def floodFillAtMouse(self, mousePos):
        startC = int(self.cameraX + (mousePos[0] / self.currentBlockSize))
        startR = int(self.cameraY + (mousePos[1] / self.currentBlockSize))
        if not (0 <= startC < self.worldSize and 0 <= startR < self.worldSize):
            return

        targetBlockMap = self.getMapPart(startC, startR, 1, 1)
        if not targetBlockMap or not targetBlockMap[0]:
            return
        targetId = targetBlockMap[0][0]
        
        newId = self.selectedBlockId
        if targetId == newId:
            return

        self._executeFloodFill(startC, startR, targetId, newId)

    def _executeFloodFill(self, startX, startY, targetId, newId):
        queue = [(startX, startY)]
        
        visited = set()
        visited.add((startX, startY))

        while queue:
            cx, cy = queue.pop()
            
            self.blockChange(cx, cy, newId)
            
            for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
                if 0 <= nx < self.worldSize and 0 <= ny < self.worldSize:
                    if (nx, ny) not in visited:
                        checkMap = self.getMapPart(nx, ny, 1, 1)
                        if checkMap and checkMap[0][0] == targetId:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
