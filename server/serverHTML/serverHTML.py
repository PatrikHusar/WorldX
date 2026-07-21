import os
import time
from flask import Flask, jsonify, request, render_template_string
import data

class ServerHTML:
    def __init__(self, host, port, game):
        imagesPath = os.path.join(os.path.dirname(__file__), 'static')
        
        self.app = Flask(__name__, static_folder=imagesPath, static_url_path='/static')
        self.host = host
        self.port = port
        self.game = game
        
        self.worldSize = data.worldSize
        self.blockList = data.getObjectList('block')
        
        self.pending_requests = []

        self.app.add_url_rule("/", "index", self.website)
        self.app.add_url_rule("/api/fullMap", "fullMap", self.getFullMapJson)
        self.app.add_url_rule("/api/entities", "entities", self.getEntitiesJson)
        self.app.add_url_rule("/api/pollEntities", "pollEntities", self.pollEntities)

    def updateEntities(self):
        responses = list(self.pending_requests)
        self.pending_requests.clear()
        for resp_fn in responses:
            try:
                resp_fn()
            except Exception:
                pass

    def pollEntities(self):
        import threading
        event = threading.Event()

        def resolve():
            event.set()

        self.pending_requests.append(resolve)
        event.wait(timeout=30.0)
        
        if resolve in self.pending_requests:
            self.pending_requests.remove(resolve)
            
        return jsonify({"status": "ok"})

    def getFullMapJson(self):
        mapViewJs = self.game.getMapPart(0, 0, self.worldSize, self.worldSize)

        fullMap = []
        for r in range(len(mapViewJs)):
            webRow = []
            for c in range(len(mapViewJs[r])):
                cell = mapViewJs[r][c]
                if cell is None:
                    webRow.append({"g": None, "zone": "unknown"})
                else:
                    groundId = None
                    if cell.get('block') and isinstance(cell['block'], dict):
                        groundId = cell['block'].get('id')
                    webRow.append({
                        "g": groundId, 
                        "zone": cell.get("zone", "unknown")
                    })
            fullMap.append(webRow)

        return jsonify({
            "map": fullMap,
            "maxSize": self.worldSize
        })
        
    def getEntitiesJson(self):
        entitiesList = []
        
        raw_players = list(self.game.getPlayersList()) if hasattr(self.game, 'getPlayersList') else []
        raw_entities = list(self.game.getEntitiesList()) if hasattr(self.game, 'getEntitiesList') else []
        
        for entityObj in raw_players + raw_entities:
            try:
                class_name = entityObj.__class__.__name__
                unique_id = getattr(entityObj, 'unique_id', getattr(entityObj, 'id', 0))
                
                type_id = unique_id
                if hasattr(entityObj, 'entity') and isinstance(entityObj.entity, dict):
                    type_id = entityObj.entity.get('id', type_id)
                elif hasattr(entityObj, 'id'):
                    type_id = entityObj.id
                
                if class_name == "Player" or entityObj in raw_players:
                    entity_type = "player"
                    eSight = int(getattr(entityObj, 'sight', 5))
                    type_id = 27 
                else:
                    entity_type = "entity"
                    eSight = getattr(entityObj, 'sight', 3)
                
                # Ak hra dynamicky mení smer alebo pridáva stav animácie, zoberieme presne to, čo posiela objekt
                eDir = getattr(entityObj, 'dir', 'south')
                eX = int(getattr(entityObj, 'x', 0))
                eY = int(getattr(entityObj, 'y', 0))
                
                if hasattr(entityObj, 'entity') and isinstance(entityObj.entity, dict):
                    eHp = entityObj.entity.get('hp', 100)
                else:
                    eHp = getattr(entityObj, 'hp', 100)

                # Ak váš systém animácií priamo generuje iný názov assetu (napr. číslo snímku), 
                # skontrolujte, či sa to nevolá inak. Štandardne držíme formát id + smer.
                asset_name = f"{type_id}{eDir}"
                
                # AK MÁTE ANIMÁCIE RIEŠENÉ CEZ ATRIBÚT (napr. entityObj.current_frame), upovedomte ma, 
                # upravili by sme riadok vyššie.
                
                entitiesList.append({
                    "id": unique_id,
                    "asset": asset_name,
                    "type": entity_type,         
                    "hp": eHp,
                    "x": float(eX),
                    "y": float(eY),
                    "sight": int(eSight)
                })
            except Exception:
                continue
            
        return jsonify(entitiesList)

    def website(self):
        htmlCode = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WorldX Map Viewer</title>
            <style>
                body { font-family: Arial, sans-serif; background: #222; color: white; text-align: center; margin: 0; padding: 5px 10px; user-select: none; overflow-y: hidden; }
                .control-panel { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 10px; margin-bottom: 10px; }
                #coordinates { font-weight: bold; color: #4CAF50; font-size: 18px; font-family: monospace; }
                .teleport-container input { padding: 6px; font-size: 13px; border: 1px solid #666; border-radius: 4px; background: #333; color: white; text-align: center; width: 120px; }
                .teleport-container button { padding: 6px 12px; font-size: 13px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px; font-weight: bold; }
                .teleport-container button:hover { background: #0b7dda; }
                
                .main-layout { display: flex; justify-content: center; align-items: flex-start; gap: 15px; max-width: 100vw; box-sizing: border-box; padding: 0 10px; }
                #canvasContainer { position: relative; }
                #gameCanvas { border: 4px solid #555; background: #000; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); cursor: grab; display: block; }
                #gameCanvas:active { cursor: grabbing; }
                
                #infoPanel { 
                    background: #333; 
                    border: 2px solid #4CAF50; 
                    border-radius: 6px; 
                    padding: 15px; 
                    width: 250px; 
                    text-align: left; 
                    font-size: 14px; 
                    box-shadow: 0px 2px 8px rgba(0,0,0,0.4); 
                    align-self: stretch;
                }
                #infoPanel h3 { margin: 0 0 10px 0; color: #4CAF50; font-size: 16px; border-bottom: 1px solid #555; padding-bottom: 5px; }
                .info-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
                .info-label { color: #aaa; font-weight: bold; }
                .info-value { color: #fff; }
                .hidden { display: none !important; }
            </style>
        </head>
        <body>
            <div class="control-panel">
                <div id="coordinates">x: 0, y: 0</div>
                <div class="teleport-container">
                    <input type="text" id="teleportPosition" placeholder="x, y (e.g., 50, 30)" onkeydown="checkEnter(event)">
                    <button onclick="teleport()">Teleport</button>
                </div>
            </div>
            
            <div class="main-layout">
                <div id="canvasContainer">
                    <canvas id="gameCanvas"></canvas>
                </div>
                
                <div id="infoPanel" class="hidden">
                    <h3>Detail entity</h3>
                    <div class="info-row"><span class="info-label">Pozícia vo svete:</span><span class="info-value" id="infoPos">x: 0, y: 0</span></div>
                    <div class="info-row"><span class="info-label">ID / Typ:</span><span class="info-value" id="infoType">N/A</span></div>
                    <div class="info-row"><span class="info-label">HP:</span><span class="info-value" id="infoHp">N/A</span></div>
                    <div class="info-row"><span class="info-label">Zóna:</span><span class="info-value" id="infoZone">N/A</span></div>
                </div>
            </div>

            <script>
                const canvas = document.getElementById('gameCanvas'); 
                const ctx = canvas.getContext('2d');
                
                const visibleColumns = 40; 
                const visibleRows = 20; 
                const baseBlockSize = 40; 
                
                let zoomLevel = 1.0;
                const minZoom = 0.4;
                const maxZoom = 2.5;
                
                let cameraC = 40.0; 
                let cameraR = 64.0; 
                let maxWorldSize = 180;
                
                let fullWorldMap = []; 
                let currentEntities = [];
                
                const discoveredTiles = {}; 
                
                let selectedEntity = null;
                
                let isDragging = false;
                let startX, startY;
                let startCameraC, startCameraR;
                let totalDragDistance = 0;

                canvas.width = visibleColumns * baseBlockSize; 
                canvas.height = visibleRows * baseBlockSize;

                const blocksConfig = {{ blocksBackend | tojson }};
                const textures = {};
                let loadedImagesCount = 0;

                const assetsToLoad = ["26"]; 
                blocksConfig.forEach(block => {
                    assetsToLoad.push(String(block.id));       
                    assetsToLoad.push(block.id + "north");    
                    assetsToLoad.push(block.id + "east");    
                    assetsToLoad.push(block.id + "south");    
                    assetsToLoad.push(block.id + "west");    
                });

                const totalAssetsCount = assetsToLoad.length;

                assetsToLoad.forEach(assetName => {
                    const img = new Image();
                    img.src = `/static/${assetName}.png`;
                    img.onload = function() {
                        loadedImagesCount++;
                        if (loadedImagesCount === totalAssetsCount) {
                            loadEntireWorld();
                        }
                    };
                    img.onerror = function() {
                        loadedImagesCount++;
                        if (loadedImagesCount === totalAssetsCount) {
                            loadEntireWorld();
                        }
                    };
                    textures[assetName] = img;
                });

                // Zabezpečíme okamžitú registráciu chýbajúcej textúry bez lagov
                function loadAndRegisterAsset(assetName) {
                    if (textures[assetName]) return;
                    
                    // Dočasne vložíme placeholder, aby sme nespúšťali sťahovanie 100x pre ten istý asset
                    textures[assetName] = "loading"; 
                    
                    const img = new Image();
                    img.src = `/static/${assetName}.png`;
                    img.onload = () => { 
                        textures[assetName] = img; 
                    };
                    img.onerror = () => { 
                        textures[assetName] = null; 
                    };
                }

                function loadEntireWorld() {
                    fetch('/api/fullMap')
                        .then(res => res.json())
                        .then(data => {
                            fullWorldMap = data.map;
                            maxWorldSize = data.maxSize;
                            loadEntitiesOnly();
                            
                            startRenderLoop();
                            startPollingLoop();
                        });
                }

                function loadEntitiesOnly() {
                    fetch('/api/entities')
                        .then(res => res.json())
                        .then(entities => {
                            currentEntities = entities;
                            
                            const player = currentEntities.find(ent => ent.type === "player");
                            if (player) {
                                const pX = Math.floor(player.x);
                                const pY = Math.floor(player.y);
                                const pSight = player.sight || 5;
                                const now = Date.now();

                                for (let dy = -pSight; dy <= pSight; dy++) {
                                    for (let dx = -pSight; dx <= pSight; dx++) {
                                        discoveredTiles[`${pX + dx},${pY + dy}`] = now;
                                    }
                                }
                            }

                            // Okamžitá kontrola a dočítanie chýbajúcich stavov animácií
                            currentEntities.forEach(ent => {
                                if (!textures[ent.asset]) {
                                    loadAndRegisterAsset(ent.asset);
                                }
                            });
                            
                            updateInfoPanel();
                        });
                }

                function startPollingLoop() {
                    fetch('/api/pollEntities')
                        .then(res => res.json())
                        .then(() => {
                            loadEntitiesOnly();
                            startPollingLoop();
                        })
                        .catch(() => {
                            setTimeout(startPollingLoop, 1000);
                        });
                }

                function startRenderLoop() {
                    renderMap();
                    requestAnimationFrame(startRenderLoop);
                }

                function renderMap() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    const drawSize = baseBlockSize * zoomLevel;

                    const colsToDraw = Math.ceil(canvas.width / drawSize) + 2;
                    const rowsToDraw = Math.ceil(canvas.height / drawSize) + 2;
                    
                    const startDrawX = Math.floor(cameraC);
                    const startDrawY = Math.floor(cameraR);

                    const player = currentEntities.find(ent => ent.type === "player");
                    const pX = player ? Math.floor(player.x) : 0;
                    const pY = player ? Math.floor(player.y) : 0;
                    const pSight = player ? player.sight : 5;
                    const now = Date.now();

                    for (let r = -1; r < rowsToDraw; r++) {
                        for (let c = -1; c < colsToDraw; c++) {
                            const wx = startDrawX + c;
                            const wy = startDrawY + r;
                            
                            if (wx < 0 || wx >= maxWorldSize || wy < 0 || wy >= maxWorldSize) continue;
                            
                            const posX = (wx - cameraC) * drawSize;
                            const posY = (wy - cameraR) * drawSize;

                            const inPlayerSight = (Math.abs(wx - pX) <= pSight && Math.abs(wy - pY) <= pSight);
                            const lastSeenTime = discoveredTiles[`${wx},${wy}`] || 0;
                            const isWithinMinute = (now - lastSeenTime <= 60000);

                            if (inPlayerSight || isWithinMinute) {
                                if (fullWorldMap[wy] && fullWorldMap[wy][wx]) {
                                    const cell = fullWorldMap[wy][wx];
                                    if (cell.g !== null && textures[cell.g] && textures[cell.g] !== "loading") {
                                        ctx.drawImage(textures[cell.g], posX, posY, drawSize, drawSize);
                                    }
                                }
                            } else {
                                if (textures["26"] && textures["26"] !== "loading") {
                                    ctx.drawImage(textures["26"], posX, posY, drawSize, drawSize);
                                } else {
                                    ctx.fillStyle = "#111"; 
                                    ctx.fillRect(posX, posY, drawSize, drawSize);
                                }
                            }
                        }
                    }

                    currentEntities.forEach(ent => {
                        const posX = (ent.x - cameraC) * drawSize;
                        const posY = (ent.y - cameraR) * drawSize;

                        if (posX + drawSize < 0 || posY + drawSize < 0 || posX > canvas.width || posY > canvas.height) return;

                        const entX = Math.floor(ent.x);
                        const entY = Math.floor(ent.y);
                        const inSight = (Math.abs(entX - pX) <= pSight && Math.abs(entY - pY) <= pSight);
                        const seenRecent = (now - (discoveredTiles[`${entX},${entY}`] || 0) <= 60000);

                        if (inSight || seenRecent || ent.type === "player") {
                            if (textures[ent.asset] && textures[ent.asset] !== "loading") {
                                ctx.drawImage(textures[ent.asset], posX, posY, drawSize, drawSize);
                            }
                        }
                    });
                }

                canvas.addEventListener('mousemove', function(e) {
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    const drawSize = baseBlockSize * zoomLevel;
                    
                    const worldX = Math.floor(cameraC + (mouseX / drawSize));
                    const worldY = Math.floor(cameraR + (mouseY / drawSize));
                    
                    if (worldX >= 0 && worldX < maxWorldSize && worldY >= 0 && worldY < maxWorldSize) {
                        document.getElementById('coordinates').innerText = `x: ${worldX}, y: ${worldY}`;
                        
                        if (selectedEntity !== null) {
                            const ent = currentEntities.find(e => e.id === selectedEntity);
                            if (ent && Math.floor(ent.x) === worldX && Math.floor(ent.y) === worldY) {
                                if (fullWorldMap[worldY] && fullWorldMap[worldY][worldX]) {
                                    document.getElementById('infoZone').innerText = fullWorldMap[worldY][worldX].zone.toUpperCase();
                                }
                            }
                        }
                    }
                });

                canvas.addEventListener('mousedown', function(e) {
                    if (e.button === 0) { 
                        isDragging = true;
                        startX = e.clientX;
                        startY = e.clientY;
                        startCameraC = cameraC;
                        startCameraR = cameraR;
                        totalDragDistance = 0;
                    }
                });

                window.addEventListener('mousemove', function(e) {
                    if (!isDragging) return;
                    
                    const drawSize = baseBlockSize * zoomLevel;
                    const dx = e.clientX - startX;
                    const dy = e.clientY - startY;
                    
                    totalDragDistance += Math.abs(dx) + Math.abs(dy);
                    
                    let newC = startCameraC - (dx / drawSize);
                    let newR = startCameraR - (dy / drawSize);
                    
                    const maxC = maxWorldSize - (visibleColumns / zoomLevel);
                    const maxR = maxWorldSize - (visibleRows / zoomLevel);
                    
                    cameraC = Math.max(0, Math.min(newC, maxC));
                    cameraR = Math.max(0, Math.min(newR, maxR));
                });

                window.addEventListener('mouseup', function(e) {
                    if (e.button === 0 && isDragging) {
                        isDragging = false;
                        if (totalDragDistance < 5) {
                            handleCanvasClick(e);
                        }
                    }
                });

                canvas.addEventListener('wheel', function(e) {
                    e.preventDefault();
                    const previousZoom = zoomLevel;
                    const zoomFactor = 1.15;
                    
                    if (e.deltaY < 0) {
                        zoomLevel = Math.min(maxZoom, zoomLevel * zoomFactor);
                    } else {
                        zoomLevel = Math.max(minZoom, zoomLevel / zoomFactor);
                    }
                    
                    if (zoomLevel === previousZoom) return;
                    
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    const gridXBefore = cameraC + (mouseX / (baseBlockSize * previousZoom));
                    const gridYBefore = cameraR + (mouseY / (baseBlockSize * previousZoom));
                    
                    const maxC = maxWorldSize - (visibleColumns / zoomLevel);
                    const maxR = maxWorldSize - (visibleRows / zoomLevel);
                    
                    cameraC = Math.max(0, Math.min(gridXBefore - (mouseX / (baseBlockSize * zoomLevel)), maxC));
                    cameraR = Math.max(0, Math.min(gridYBefore - (mouseY / (baseBlockSize * zoomLevel)), maxR));
                });

                function handleCanvasClick(e) {
                    const rect = canvas.getBoundingClientRect();
                    const clickX = e.clientX - rect.left;
                    const clickY = e.clientY - rect.top;
                    const drawSize = baseBlockSize * zoomLevel;
                    const clickWorldX = cameraC + (clickX / drawSize);
                    const clickWorldY = cameraR + (clickY / drawSize);
                    
                    const clickedEntity = currentEntities.find(ent => {
                        return Math.abs(ent.x + 0.5 - clickWorldX) <= 0.5 && 
                               Math.abs(ent.y + 0.5 - clickWorldY) <= 0.5;
                    });
                    
                    if (clickedEntity) {
                        selectedEntity = clickedEntity.id;
                        showEntityDetails(clickedEntity);
                    } else {
                        selectedEntity = null;
                        document.getElementById('infoPanel').classList.add('hidden');
                    }
                }

                function showEntityDetails(ent) {
                    const infoPanel = document.getElementById('infoPanel');
                    document.getElementById('infoPos').innerText = `x: ${ent.x.toFixed(2)}, y: ${ent.y.toFixed(2)}`;
                    
                    const ex = Math.floor(ent.x);
                    const ey = Math.floor(ent.y);
                    let zoneName = "UNKNOWN";
                    if (fullWorldMap[ey] && fullWorldMap[ey][ex]) {
                        zoneName = fullWorldMap[ey][ex].zone || "UNKNOWN";
                    }
                    
                    document.getElementById('infoZone').innerText = zoneName.toUpperCase();
                    document.getElementById('infoType').innerText = `ID: ${ent.id} (${ent.type})`;
                    document.getElementById('infoHp').innerText = ent.hp;
                    infoPanel.classList.remove('hidden');
                }

                function updateInfoPanel() {
                    if (selectedEntity === null) return;
                    const ent = currentEntities.find(e => e.id === selectedEntity);
                    if (ent) {
                        showEntityDetails(ent);
                    } else {
                        selectedEntity = null;
                        document.getElementById('infoPanel').classList.add('hidden');
                    }
                }

                function checkEnter(e) { if (e.key === 'Enter') teleport(); }
                
                function teleport() {
                    const input = document.getElementById('teleportPosition').value; 
                    const parts = input.split(','); 
                    if (parts.length !== 2) return;
                    
                    let targetX = parseInt(parts[0].trim()); 
                    let targetY = parseInt(parts[1].trim()); 
                    if (isNaN(targetX) || isNaN(targetY)) return;
                    
                    const maxC = maxWorldSize - (visibleColumns / zoomLevel); 
                    const maxR = maxWorldSize - (visibleRows / zoomLevel);
                    
                    cameraC = Math.max(0, Math.min(targetX, maxC)); 
                    cameraR = Math.max(0, Math.min(targetY, maxR)); 
                }
            </script>
        </body>
        </html>
        """
        return render_template_string(htmlCode, blocksBackend=self.blockList)
    
    def startServer(self):
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)