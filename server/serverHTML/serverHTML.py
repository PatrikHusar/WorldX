import os
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
                        groundId = cell['block'].get('typeId', cell['block'].get('id'))
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
                unique_id = getattr(entityObj, 'playerId', getattr(entityObj, 'entityId', getattr(entityObj, 'id', 0)))
                
                type_id = unique_id
                if hasattr(entityObj, 'entity') and isinstance(entityObj.entity, dict):
                    type_id = entityObj.entity.get('typeId', entityObj.entity.get('id', type_id))
                elif hasattr(entityObj, 'typeId'):
                    type_id = entityObj.typeId
                elif hasattr(entityObj, 'id'):
                    type_id = entityObj.id
                
                if class_name == "Player" or entityObj in raw_players:
                    entity_type = "player"
                    eSight = int(getattr(entityObj, 'player', {}).get('sight', getattr(entityObj, 'sight', 5)))
                    type_id = 27
                else:
                    entity_type = "entity"
                    eSight = getattr(entityObj, 'sight', 3)
                
                eDir = getattr(entityObj, 'dir', 'south')
                
                eX = float(getattr(entityObj, 'x', 0.0))
                eY = float(getattr(entityObj, 'y', 0.0))
                
                if hasattr(entityObj, 'entity') and isinstance(entityObj.entity, dict):
                    eHp = entityObj.entity.get('health', entityObj.entity.get('hp', 100))
                else:
                    eHp = getattr(entityObj, 'health', getattr(entityObj, 'hp', 100))

                if hasattr(entityObj, 'entity') and isinstance(entityObj.entity, dict):
                    eEquipped = entityObj.entity.get('equipped', {})
                else:
                    eEquipped = getattr(entityObj, 'equipped', {})

                if hasattr(entityObj, 'entity') and isinstance(entityObj.entity, dict):
                    eInventory = entityObj.entity.get('inventory', [])
                else:
                    eInventory = getattr(entityObj, 'inventory', [])

                asset_name = f"{type_id}{eDir}"
                
                entitiesList.append({
                    "id": unique_id,
                    "asset": asset_name,
                    "type": entity_type,
                    "hp": eHp,
                    "equipped": eEquipped,
                    "inventory": eInventory,
                    "x": eX,
                    "y": eY,
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
                * { box-sizing: border-box; }
                html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; background: #222; color: white; font-family: Arial, sans-serif; user-select: none; }
                body { display: flex; flex-direction: column; }
                
                .control-panel { display: flex; justify-content: center; align-items: center; padding: 10px; background: #1a1a1a; flex-shrink: 0; }
                .control-panel h1 { margin: 0; font-size: 20px; color: #4CAF50; letter-spacing: 1px; }

                .main-layout { position: relative; width: 100%; height: calc(100% - 45px); padding: 5px; }
                #canvasContainer { width: 100%; height: 100%; position: relative; display: flex; justify-content: center; align-items: center; background: #000; border: 2px solid #555; overflow: hidden; }
                #gameCanvas { cursor: grab; display: block; }
                #gameCanvas:active { cursor: grabbing; }
                
                #coordinates { 
                    position: absolute;
                    top: 15px;
                    left: 15px;
                    z-index: 10;
                    font-weight: bold; 
                    color: #4CAF50; 
                    font-size: 15px; 
                    font-family: monospace; 
                    background: #000000;
                    padding: 5px 10px;
                    border-radius: 4px;
                    border: 1px solid #4CAF50;
                }

                #playersPanel {
                    position: absolute;
                    top: 55px;
                    left: 15px;
                    z-index: 10;
                    background: rgba(30, 30, 30, 0.9);
                    border: 2px solid #4CAF50;
                    border-radius: 6px;
                    padding: 12px;
                    width: 220px;
                    max-height: calc(100% - 80px);
                    overflow-y: auto;
                    box-shadow: 0px 4px 12px rgba(0,0,0,0.6);
                    backdrop-filter: blur(4px);
                }
                #playersPanel h3 { margin: 0 0 10px 0; color: #4CAF50; font-size: 16px; border-bottom: 1px solid #555; padding-bottom: 5px; }
                .player-item { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; background: rgba(255, 255, 255, 0.05); padding: 6px 8px; border-radius: 4px; }
                .player-item span { font-weight: bold; font-size: 13px; color: #fff; }
                .teleport-btn { padding: 4px 8px; font-size: 12px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
                .teleport-btn:hover { background: #388E3C; }

                #infoPanel { 
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    z-index: 10;
                    background: rgba(30, 30, 30, 0.9); 
                    border: 2px solid #4CAF50; 
                    border-radius: 6px; 
                    padding: 15px; 
                    width: 250px; 
                    text-align: left; 
                    font-size: 14px; 
                    box-shadow: 0px 4px 12px rgba(0,0,0,0.6); 
                    backdrop-filter: blur(4px);
                }
                #infoPanel h3 { margin: 0 0 10px 0; color: #4CAF50; font-size: 16px; border-bottom: 1px solid #555; padding-bottom: 5px; }
                .info-row { display: flex; flex-direction: column; margin-bottom: 8px; }
                .info-row-inline { display: flex; justify-content: space-between; margin-bottom: 5px; }
                .info-label { color: #aaa; font-weight: bold; }
                .info-value { color: #fff; word-break: break-word; }
                .hidden { display: none !important; }
            </style>
        </head>
        <body>
            <div class="control-panel">
                <h1>WorldX</h1>
            </div>
            
            <div class="main-layout">
                <div id="canvasContainer">
                    <canvas id="gameCanvas"></canvas>
                </div>
                
                <div id="coordinates">x: 0, y: 0</div>

                <div id="playersPanel">
                    <h3>Players List</h3>
                    <div id="playersListContainer"></div>
                </div>
                
                <div id="infoPanel" class="hidden">
                    <h3 id="infoTitle">Entity Details</h3>
                    
                    <div class="info-row-inline"><span class="info-label">HP:</span><span class="info-value" id="infoHp">N/A</span></div>
                    
                    <div id="zoneRow" class="info-row-inline"><span class="info-label">Zone:</span><span class="info-value" id="infoZone">N/A</span></div>
                    
                    <div id="playerOnlyStats">
                        <div class="info-row">
                            <span class="info-label">Equipped:</span>
                            <span class="info-value" id="infoEquipped">Nothing</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Inventory:</span>
                            <span class="info-value" id="infoInventory">Empty</span>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                const canvas = document.getElementById('gameCanvas'); 
                const canvasContainer = document.getElementById('canvasContainer');
                const ctx = canvas.getContext('2d');
                
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
                let currentlyVisibleTiles = new Set();

                let selectedEntity = null;
                let followedPlayerId = null;

                const fogRevealTimeoutMs = 60000;
                
                let isDragging = false;
                let startX, startY;
                let startCameraC, startCameraR;
                let totalDragDistance = 0;
                
                let lastTime = performance.now();

                function resizeCanvas() {
                    canvas.width = canvasContainer.clientWidth;
                    canvas.height = canvasContainer.clientHeight;
                }
                window.addEventListener('resize', resizeCanvas);
                resizeCanvas();

                const blocksConfig = {{ blocksBackend | tojson }};
                const textures = {};
                let loadedImagesCount = 0;

                const assetsToLoad = ["26", "27", "27north", "27east", "27south", "27west"]; 
                blocksConfig.forEach(block => {
                    const bId = (block.typeId !== undefined) ? block.typeId : block.id;
                    if (bId !== undefined) {
                        assetsToLoad.push(String(bId));       
                        assetsToLoad.push(bId + "north");    
                        assetsToLoad.push(bId + "east");    
                        assetsToLoad.push(bId + "south");    
                        assetsToLoad.push(bId + "west");
                    }
                });

                const totalAssetsCount = assetsToLoad.length;

                assetsToLoad.forEach(assetName => {
                    const img = new Image();
                    img.src = `/static/${assetName}.png`;
                    img.onload = function() {
                        textures[assetName] = img;
                        checkAllLoaded();
                    };
                    img.onerror = function() {
                        textures[assetName] = null;
                        checkAllLoaded();
                    };
                });

                function checkAllLoaded() {
                    loadedImagesCount++;
                    if (loadedImagesCount === totalAssetsCount) {
                        loadEntireWorld();
                    }
                }

                function loadAndRegisterAsset(assetName) {
                    if (textures[assetName] !== undefined) return;
                    textures[assetName] = "loading"; 
                    
                    const img = new Image();
                    img.src = `/static/${assetName}.png`;
                    img.onload = () => { textures[assetName] = img; };
                    img.onerror = () => { textures[assetName] = null; };
                }

                function loadEntireWorld() {
                    fetch('/api/fullMap')
                        .then(res => {
                            if (!res.ok) throw new Error("Server is restarting...");
                            return res.json();
                        })
                        .then(data => {
                            for (let member in discoveredTiles) delete discoveredTiles[member];

                            fullWorldMap = data.map;
                            maxWorldSize = data.maxSize;
                            
                            loadEntitiesOnly();
                            startRenderLoop(performance.now());
                            startPollingLoop();
                        })
                        .catch(err => {
                            setTimeout(loadEntireWorld, 2000);
                        });
                }

                function loadEntitiesOnly() {
                    fetch('/api/entities')
                        .then(res => res.json())
                        .then(newEntities => {
                            const updatedIds = new Set();

                            newEntities.forEach(nEnt => {
                                updatedIds.add(nEnt.id);
                                let existing = currentEntities.find(e => e.id === nEnt.id);
                                
                                if (existing) {
                                    existing.targetX = Number(nEnt.x);
                                    existing.targetY = Number(nEnt.y);
                                    existing.asset = nEnt.asset;
                                    existing.hp = nEnt.hp;
                                    existing.equipped = nEnt.equipped;
                                    existing.inventory = nEnt.inventory;
                                    existing.sight = nEnt.sight;
                                    existing.type = nEnt.type;
                                } else {
                                    nEnt.x = Number(nEnt.x);
                                    nEnt.y = Number(nEnt.y);
                                    nEnt.targetX = nEnt.x;
                                    nEnt.targetY = nEnt.y;
                                    currentEntities.push(nEnt);
                                }
                                
                                loadAndRegisterAsset(nEnt.asset);
                            });

                            currentEntities = currentEntities.filter(e => updatedIds.has(e.id));

                            const playersList = currentEntities.filter(ent => ent.type === "player");
                            const now = Date.now();

                            currentlyVisibleTiles.clear();

                            playersList.forEach(player => {
                                const pX = Math.round(player.x);
                                const pY = Math.round(player.y);
                                const pSight = player.sight || 5;

                                for (let dy = -pSight; dy <= pSight; dy++) {
                                    for (let dx = -pSight; dx <= pSight; dx++) {
                                        const key = `${pX + dx},${pY + dy}`;
                                        currentlyVisibleTiles.add(key);
                                        discoveredTiles[key] = now;
                                    }
                                }
                            });
                            
                            updateInfoPanel();
                            renderPlayersList(playersList);
                        });
                }

                function renderPlayersList(players) {
                    const container = document.getElementById('playersListContainer');
                    container.innerHTML = '';

                    if (players.length === 0) {
                        container.innerHTML = '<div style="color: #aaa; font-style: italic; font-size: 13px;">No players online</div>';
                        return;
                    }

                    players.forEach(p => {
                        const item = document.createElement('div');
                        item.className = 'player-item';

                        const label = document.createElement('span');
                        label.innerText = `Player ${p.id}`;

                        const btn = document.createElement('button');
                        btn.className = 'teleport-btn';
                        btn.innerText = 'Teleport';
                        btn.onclick = () => teleportToPlayer(p.id);

                        item.appendChild(label);
                        item.appendChild(btn);
                        container.appendChild(item);
                    });
                }

                function centerCameraOn(x, y) {
                    const drawSize = baseBlockSize * zoomLevel;
                    const visibleCols = canvas.width / drawSize;
                    const visibleRows = canvas.height / drawSize;

                    cameraC = Math.max(0, Math.min(x - (visibleCols / 2), maxWorldSize - 1));
                    cameraR = Math.max(0, Math.min(y - (visibleRows / 2), maxWorldSize - 1));
                }

                function teleportToPlayer(playerId) {
                    followedPlayerId = playerId;
                    const p = currentEntities.find(e => e.id === playerId);
                    if (p) {
                        centerCameraOn(p.x, p.y);
                    }
                }

                function startPollingLoop() {
                    fetch('/api/pollEntities')
                        .then(res => {
                            if (!res.ok) throw new Error("Server unavailable");
                            return res.json();
                        })
                        .then(() => {
                            loadEntitiesOnly();
                            startPollingLoop();
                        })
                        .catch(() => {
                            setTimeout(loadEntireWorld, 2000);
                        });
                }

                function startRenderLoop(nowTime) {
                    const dt = Math.min((nowTime - lastTime) / 1000, 0.1) || 0;
                    lastTime = nowTime;

                    renderMap(dt);
                    requestAnimationFrame(startRenderLoop);
                }

                function drawAnimatedEntity(ent, posX, posY, drawSize) {
                    let img = textures[ent.asset];

                    if (!img || img === "loading") {
                        const baseAsset = ent.asset.replace(/(north|south|east|west)/g, '');
                        img = textures[baseAsset];
                    }

                    if (img && img !== "loading") {
                        ctx.drawImage(img, posX, posY, drawSize, drawSize);
                    } else {
                        ctx.beginPath();
                        ctx.arc(posX + drawSize / 2, posY + drawSize / 2, drawSize * 0.4, 0, 2 * Math.PI);
                        ctx.fillStyle = (ent.type === "player") ? "#4CAF50" : "#F44336";
                        ctx.fill();
                        ctx.lineWidth = 2;
                        ctx.strokeStyle = "#FFFFFF";
                        ctx.stroke();
                    }
                }

                function renderMap(dt) {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    const drawSize = baseBlockSize * zoomLevel;

                    const lerpSpeed = 10.0;
                    currentEntities.forEach(ent => {
                        if (ent.targetX !== undefined && !isNaN(ent.targetX)) {
                            ent.x += (ent.targetX - ent.x) * Math.min(dt * lerpSpeed, 1.0);
                        }
                        if (ent.targetY !== undefined && !isNaN(ent.targetY)) {
                            ent.y += (ent.targetY - ent.y) * Math.min(dt * lerpSpeed, 1.0);
                        }
                    });

                    if (followedPlayerId !== null && !isDragging) {
                        const fPlayer = currentEntities.find(e => e.id === followedPlayerId);
                        if (fPlayer) {
                            centerCameraOn(fPlayer.x, fPlayer.y);
                        }
                    }

                    const colsToDraw = Math.ceil(canvas.width / drawSize) + 2;
                    const rowsToDraw = Math.ceil(canvas.height / drawSize) + 2;
                    
                    const startDrawX = Math.floor(cameraC);
                    const startDrawY = Math.floor(cameraR);

                    const now = Date.now();

                    for (let r = -1; r < rowsToDraw; r++) {
                        for (let c = -1; c < colsToDraw; c++) {
                            const wx = startDrawX + c;
                            const wy = startDrawY + r;
                            
                            if (wx < 0 || wx >= maxWorldSize || wy < 0 || wy >= maxWorldSize) continue;
                            
                            const posX = (wx - cameraC) * drawSize;
                            const posY = (wy - cameraR) * drawSize;

                            if (fullWorldMap[wy] && fullWorldMap[wy][wx]) {
                                const cell = fullWorldMap[wy][wx];
                                if (cell.g !== null && textures[cell.g] && textures[cell.g] !== "loading") {
                                    ctx.drawImage(textures[cell.g], posX, posY, drawSize, drawSize);
                                }
                            }
                        }
                    }

                    const playersList = currentEntities.filter(e => e.type === "player");
                    playersList.forEach(ent => {
                        const posX = (ent.x - cameraC) * drawSize;
                        const posY = (ent.y - cameraR) * drawSize;

                        if (posX + drawSize >= 0 && posY + drawSize >= 0 && posX <= canvas.width && posY <= canvas.height) {
                            drawAnimatedEntity(ent, posX, posY, drawSize);
                        }
                    });

                    const otherEntitiesList = currentEntities.filter(e => e.type !== "player");
                    otherEntitiesList.forEach(ent => {
                        const posX = (ent.x - cameraC) * drawSize;
                        const posY = (ent.y - cameraR) * drawSize;

                        if (posX + drawSize >= 0 && posY + drawSize >= 0 && posX <= canvas.width && posY <= canvas.height) {
                            const entX = Math.round(ent.x);
                            const entY = Math.round(ent.y);
                            const key = `${entX},${entY}`;
                            
                            const inSight = currentlyVisibleTiles.has(key);
                            const seenRecent = (now - (discoveredTiles[key] || 0) <= fogRevealTimeoutMs);

                            if (inSight || seenRecent) {
                                drawAnimatedEntity(ent, posX, posY, drawSize);
                            }
                        }
                    });

                    for (let r = -1; r < rowsToDraw; r++) {
                        for (let c = -1; c < colsToDraw; c++) {
                            const wx = startDrawX + c;
                            const wy = startDrawY + r;
                            
                            if (wx < 0 || wx >= maxWorldSize || wy < 0 || wy >= maxWorldSize) continue;
                            
                            const posX = (wx - cameraC) * drawSize;
                            const posY = (wy - cameraR) * drawSize;

                            const key = `${wx},${wy}`;
                            const inPlayerSight = currentlyVisibleTiles.has(key);
                            const lastSeenTime = discoveredTiles[key] || 0;
                            const isVisible = inPlayerSight || (now - lastSeenTime <= fogRevealTimeoutMs);

                            if (!isVisible) {
                                if (textures["26"] && textures["26"] !== "loading") {
                                    ctx.drawImage(textures["26"], posX, posY, drawSize, drawSize);
                                } else {
                                    ctx.fillStyle = "#111"; 
                                    ctx.fillRect(posX, posY, drawSize, drawSize);
                                }
                            }
                        }
                    }
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

                    if (totalDragDistance > 5) {
                        followedPlayerId = null;
                    }
                    
                    let newC = startCameraC - (dx / drawSize);
                    let newR = startCameraR - (dy / drawSize);
                    
                    cameraC = Math.max(0, Math.min(newC, maxWorldSize - 1));
                    cameraR = Math.max(0, Math.min(newR, maxWorldSize - 1));
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
                    
                    cameraC = Math.max(0, Math.min(gridXBefore - (mouseX / (baseBlockSize * zoomLevel)), maxWorldSize - 1));
                    cameraR = Math.max(0, Math.min(gridYBefore - (mouseY / (baseBlockSize * zoomLevel)), maxWorldSize - 1));
                });

                function handleCanvasClick(e) {
                    const rect = canvas.getBoundingClientRect();
                    const clickX = e.clientX - rect.left;
                    const clickY = e.clientY - rect.top;
                    const drawSize = baseBlockSize * zoomLevel;
                    const clickWorldX = cameraC + (clickX / drawSize);
                    const clickWorldY = cameraR + (clickY / drawSize);
                    
                    const clickedEntity = currentEntities.find(ent => {
                        return Math.abs(ent.x + 0.5 - clickWorldX) <= 0.8 && 
                               Math.abs(ent.y + 0.5 - clickWorldY) <= 0.8;
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
                    const zoneRow = document.getElementById('zoneRow');
                    const playerStats = document.getElementById('playerOnlyStats');
                    const infoTitle = document.getElementById('infoTitle');

                    document.getElementById('infoHp').innerText = ent.hp;

                    if (ent.type === 'player') {
                        infoTitle.innerText = `Player ${ent.id}`;
                        zoneRow.classList.add('hidden');
                        playerStats.classList.remove('hidden');

                        let eqText = "Nothing";
                        if (ent.equipped && typeof ent.equipped === 'object' && Object.keys(ent.equipped).length > 0) {
                            if (Array.isArray(ent.equipped)) {
                                eqText = ent.equipped.join(', ');
                            } else {
                                eqText = Object.entries(ent.equipped).map(([slot, item]) => `${slot}: ${item}`).join(', ');
                            }
                        }
                        document.getElementById('infoEquipped').innerText = eqText;

                        let invText = "Empty";
                        if (ent.inventory && Array.isArray(ent.inventory) && ent.inventory.length > 0) {
                            invText = ent.inventory.join(', ');
                        } else if (ent.inventory && typeof ent.inventory === 'object' && Object.keys(ent.inventory).length > 0) {
                            invText = Object.values(ent.inventory).join(', ');
                        }
                        document.getElementById('infoInventory').innerText = invText;

                    } else {
                        infoTitle.innerText = "Entity Details";
                        zoneRow.classList.remove('hidden');
                        playerStats.classList.add('hidden');

                        const ex = Math.floor(ent.x);
                        const ey = Math.floor(ent.y);
                        let zoneName = "UNKNOWN";
                        if (fullWorldMap[ey] && fullWorldMap[ey][ex]) {
                            zoneName = fullWorldMap[ey][ex].zone || "UNKNOWN";
                        }
                        
                        document.getElementById('infoZone').innerText = zoneName.toUpperCase();
                    }

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
            </script>
        </body>
        </html>
        """
        return render_template_string(htmlCode, blocksBackend=self.blockList)
    
    def startServer(self):
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)