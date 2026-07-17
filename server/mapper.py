import pygame
import sys
import os
import data
from PIL import Image as PILImage

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
        
        self.cameraX, self.cameraY = float(data.spawnPos[0]), float(data.spawnPos[1])
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
            bId = block['id']
            bName = idToName.get(bId, f"unknown_{bId}")
            self.textures[bId] = self._loadTexture(os.path.join(staticDir, f"{bName}.png"), (120, 50, 50))

        self.entityTextures = {}
        for eId, eName in idToName.items():
            self.entityTextures[eId] = {}
            for direction in ['north', 'east', 'south', 'west']:
                imgPath = os.path.join(staticDir, f"{eName}{direction}.png")
                self.entityTextures[eId][direction] = self._loadTexture(imgPath, (255, 235, 59), (32, 32))

    def _loadTexture(self, imgPath, fallbackColor, fallbackSize=(32, 32)):
        if os.path.exists(imgPath):
            try:
                pilImg = PILImage.open(imgPath).convert("RGBA")
                return pygame.image.fromstring(pilImg.tobytes(), pilImg.size, "RGBA").convert_alpha()
            except Exception:
                pass
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
            ':': [(0.5,0.4,0.5,0.5), (0.5,1.4,0.5,1.5)], ',': [(0.5,1.5,0.3,1.9)], ' ': [],
            '-': [(0.2,1,0.8,1)], '_': [(0,2,1,2)], 'h': [(0,0,0,2), (0,1,1,1), (1,1,1,2)],
            'r': [(0,0,0,2), (0,0.5,1,0.5)], 'a': [(0,1,1,1), (1,0,1,2), (0,0,1,0), (0,2,1,2)],
            'c': [(1,0,0,0), (0,0,0,2), (0,2,1,2)], 'z': [(0,0,1,0), (1,0,0,2), (0,2,1,2)],
            'i': [(0.5,0,0.5,0.2), (0.5,0.5,0.5,2)], 'v': [(0,0,0.5,2), (1,0,0.5,2)],
            'o': [(0,0,1,0), (1,0,1,2), (1,2,0,2), (0,2,0,0)], 'n': [(0,0,0,2), (0,0,1,0), (1,0,1,2)],
            't': [(0.5,0,0.5,2), (0.1,0.5,0.9,0.5)], 'e': [(1,2,0,2), (0,2,0,0), (0,0,1,0), (0,1,1,1)],
            'd': [(0,0,0,2), (0,0,1,0), (1,0,1,2), (0,2,1,2)], 'p': [(0,0,0,2), (0,0,1,0), (1,0,1,1), (0,1,1,1)]
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
            mapAreaWidth = self.screenWidth - 120
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    self.handleTeleport()
                elif event.type == pygame.MOUSEWHEEL:
                    if mousePos[0] >= mapAreaWidth:
                        if event.y > 0: self.sidebarScrollY = min(0, self.sidebarScrollY + 30)
                        else: self.sidebarScrollY = max(-max(0, (len(self.blockList) * 65 + 60) - self.screenHeight), self.sidebarScrollY - 30)
                    else:
                        self.handleZoom(1 if event.y > 0 else -1, mousePos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  
                        if mousePos[0] < mapAreaWidth:
                            clickedEntity = self.checkEntityClick(mousePos)
                            if clickedEntity:
                                self.selectedEntity = clickedEntity
                                self.isDrawing = False
                            else:
                                self.selectedEntity = None
                                if pygame.key.get_pressed()[pygame.K_LSHIFT]: self.floodFillAtMouse(mousePos)
                                else:
                                    self.isDrawing = True
                                    self.drawBlockAtMouse(mousePos)
                        else:
                            self.checkSidebarClick(mousePos)
                    elif event.button == 3:
                        self.isPanning = True
                        pygame.mouse.get_rel()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1: self.isDrawing = False
                    elif event.button == 3: self.isPanning = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.isDrawing and mousePos[0] < mapAreaWidth:
                        self.drawBlockAtMouse(mousePos)
                    elif self.isPanning:
                        relX, relY = pygame.mouse.get_rel()
                        self.cameraX -= relX / self.currentBlockSize
                        self.cameraY -= relY / self.currentBlockSize
                        self.clampCamera()

            colsToLoad = int(mapAreaWidth / self.currentBlockSize) + 2
            rowsToLoad = int(self.screenHeight / self.currentBlockSize) + 2
            
            currentMapView = self.getMapPart(int(self.cameraX), int(self.cameraY), colsToLoad, rowsToLoad)
            self.screen.fill((34, 34, 34)) 
            
            offsetX = int((self.cameraX - int(self.cameraX)) * self.currentBlockSize)
            offsetY = int((self.cameraY - int(self.cameraY)) * self.currentBlockSize)
            
            # Vykresľovanie vrstiev (Ground a Object)
            for rIdx, row in enumerate(currentMapView):
                for cIdx, cell in enumerate(row):
                    xPos = cIdx * self.currentBlockSize - offsetX
                    yPos = rIdx * self.currentBlockSize - offsetY
                    
                    if xPos < mapAreaWidth and yPos < self.screenHeight:
                        # 🟢 KONTROLA: Vykresľujeme iba ak políčko existuje (nie je None na okraji mapy)
                        if cell is not None:
                            # Vrstva 1: Podklad (Ground)
                            if cell.get('ground'):
                                gTex = self.textures.get(cell['ground']['id'])
                                if gTex:
                                    self.screen.blit(pygame.transform.scale(gTex, (self.currentBlockSize, self.currentBlockSize)), (xPos, yPos))
                            
                            # Vrstva 2: Statické Objekty (Steny, Truhly)
                            if cell.get('object') and cell['object'].get('type') == 'block':
                                oTex = self.textures.get(cell['object']['id'])
                                if oTex:
                                    self.screen.blit(pygame.transform.scale(oTex, (self.currentBlockSize, self.currentBlockSize)), (xPos, yPos))
            # Samostatné plynulé kreslenie entít z registra na ich desatinných pozíciách
            for entity in self.entities:
                eScreenX = int((entity.x - self.cameraX) * self.currentBlockSize)
                eScreenY = int((entity.y - self.cameraY) * self.currentBlockSize)
                
                if 0 <= eScreenX < mapAreaWidth and 0 <= eScreenY < self.screenHeight:
                    eId = entity.entity['id']
                    eDir = getattr(entity, 'dir', 'north')
                    tex = self.entityTextures.get(eId, {}).get(eDir)
                    if tex:
                        self.screen.blit(pygame.transform.scale(tex, (self.currentBlockSize, self.currentBlockSize)), (eScreenX, eScreenY))

            self.renderSidebar()
            self.renderCoordinates()
            self.renderEntityStats()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def handleTeleport(self):
        try:
            vstup = input("Zadaj suradnice 'x, y': ")
            casti = vstup.split(",")
            if len(casti) == 2:
                self.cameraX, self.cameraY = float(casti[0].strip()), float(casti[1].strip())
                self.clampCamera()
        except Exception:
            pass

    def handleZoom(self, direction, mousePos):
        wX, wY = self.cameraX + (mousePos[0] / self.currentBlockSize), self.cameraY + (mousePos[1] / self.currentBlockSize)
        newSize = self.currentBlockSize + (direction * 4)
        if 10 <= newSize <= 80:
            self.currentBlockSize = newSize
            self.cameraX, self.cameraY = wX - (mousePos[0] / newSize), wY - (mousePos[1] / newSize)
            self.clampCamera()

    def drawBlockAtMouse(self, mousePos):
        clickC = int(self.cameraX + (mousePos[0] / self.currentBlockSize))
        clickR = int(self.cameraY + (mousePos[1] / self.currentBlockSize))
        if 0 <= clickC < self.worldSize and 0 <= clickR < self.worldSize:
            self.blockChange(clickC, clickR, self.selectedBlockId)

    def clampCamera(self):
        maxCols = (self.screenWidth - 120) / self.currentBlockSize
        maxRows = self.screenHeight / self.currentBlockSize
        self.cameraX = max(0.0, min(self.cameraX, self.worldSize - maxCols))
        self.cameraY = max(0.0, min(self.cameraY, self.worldSize - maxRows))

    def renderSidebar(self):
        sidebarX = self.screenWidth - 120
        sidebarSurf = pygame.Surface((120, self.screenHeight))
        sidebarSurf.fill((51, 51, 51))
        
        for idx, block in enumerate(self.blockList):
            bId = block['id']
            btnY = 45 + (idx * 65) + self.sidebarScrollY
            if -60 <= btnY <= self.screenHeight:
                btnRect = pygame.Rect(20, btnY, 80, 55)
                bColor = (76, 175, 80) if bId == self.selectedBlockId else (102, 102, 102)
                pygame.draw.rect(sidebarSurf, (68, 68, 68), btnRect)
                pygame.draw.rect(sidebarSurf, bColor, btnRect, 2)
                tex = self.textures.get(bId)
                if tex: sidebarSurf.blit(pygame.transform.scale(tex, (32, 32)), (44, btnY + 5))
        
        self.screen.blit(sidebarSurf, (sidebarX, 0))
        pygame.draw.line(self.screen, (85, 85, 85), (sidebarX, 0), (sidebarX, self.screenHeight), 4)
        pygame.draw.rect(self.screen, (51, 51, 51), (sidebarX + 2, 0, 116, 40))
        self.drawCustomText("bloky", sidebarX + 25, 12, (170, 170, 170), 1.5)
        
        for idx, block in enumerate(self.blockList):
            btnY = 45 + (idx * 65) + self.sidebarScrollY
            if 40 <= btnY <= self.screenHeight - 20:
                self.drawCustomText(self.idToName.get(block['id'], "block")[:6], sidebarX + 25, btnY + 40, (255, 255, 255), 1)

    def checkSidebarClick(self, mousePos):
        sidebarX = self.screenWidth - 120
        for idx, block in enumerate(self.blockList):
            btnY = 45 + (idx * 65) + self.sidebarScrollY
            if pygame.Rect(sidebarX + 20, btnY, 80, 55).collidepoint(mousePos) and btnY >= 40:
                self.selectedBlockId = block['id']
                break

    def renderCoordinates(self):
        mousePos = pygame.mouse.get_pos()
        if mousePos[0] < self.screenWidth - 120:
            cC = int(self.cameraX + (mousePos[0] / self.currentBlockSize))
            cR = int(self.cameraY + (mousePos[1] / self.currentBlockSize))
            if 0 <= cC < self.worldSize and 0 <= cR < self.worldSize:
                txt = f"x:{cC}, y:{cR}"
                pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(10, 10, len(txt)*11 + 10, 26))
                self.drawCustomText(txt, 15, 14, (76, 175, 80), 1.5)
    
    def checkEntityClick(self, mousePos):
        for ent in self.entities:
            eX = int((ent.x - self.cameraX) * self.currentBlockSize)
            eY = int((ent.y - self.cameraY) * self.currentBlockSize)
            if pygame.Rect(eX, eY, self.currentBlockSize, self.currentBlockSize).collidepoint(mousePos):
                return ent
        return None

    def renderEntityStats(self):
        if not self.selectedEntity:
            return
        ent = self.selectedEntity
        eType = ent.entity.get('type', 'enemy')
        eName = self.idToName.get(ent.entity['id'], "unknown").upper()
        
        statsLines = []
        if eType == 'player':
            statsLines.append(f"--- hrac: {eName} ---")
            statsLines.append(f"hp: {ent.health}")
            statsLines.append("")
            statsLines.append("--- inventar ---")
            inv = ent.entity['properties'].get('inventory', [])
            if not inv: statsLines.append("  (prazdny)")
            for item in inv: statsLines.append(f"  - {item}")
        else:
            statsLines = [
                f"--- {eName} ---",
                f"hp: {ent.health}",
                f"dmg: {ent.damage}",
                f"speed: {ent.speed}",
                f"behavior: {ent.behaviour}",
                f"dir: {ent.dir}",
                f"pos: {int(ent.x)}, {int(ent.y)}"
            ]
        
        bgRect = pygame.Rect(10, 45, 200, len(statsLines) * 20 + 15)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bgRect)
        pygame.draw.rect(self.screen, (76, 175, 80), bgRect, 1)
        
        startY = 55
        for line in statsLines:
            self.drawCustomText(line, 20, startY, (255, 255, 255), 1.2)
            startY += 20

    def floodFillAtMouse(self, mousePos):
        sC = int(self.cameraX + (mousePos[0] / self.currentBlockSize))
        sR = int(self.cameraY + (mousePos[1] / self.currentBlockSize))
        if 0 <= sC < self.worldSize and 0 <= sR < self.worldSize:
            cell = self.getMapPart(sC, sR, 1, 1)[0][0]
            targetId = cell['ground']['id'] # Flood fill pracuje s podkladovou vrstvou
            if targetId != self.selectedBlockId:
                self._executeFloodFill(sC, sR, targetId, self.selectedBlockId)

    def _executeFloodFill(self, startX, startY, targetId, newId):
        queue = [(startX, startY)]
        visited = {(startX, startY)}
        while queue:
            cx, cy = queue.pop()
            self.blockChange(cx, cy, newId)
            for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
                if 0 <= nx < self.worldSize and 0 <= ny < self.worldSize and (nx, ny) not in visited:
                    if self.getMapPart(nx, ny, 1, 1)[0][0]['ground']['id'] == targetId:
                        visited.add((nx, ny))
                        queue.append((nx, ny))