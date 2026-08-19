import os
import threading
from flask import Flask, jsonify, request, render_template_string
import data
import inventory

class ServerHTML:
    def __init__(self, host, port, game):
        imagesPath = os.path.join(os.path.dirname(__file__), 'static')
        
        self.app = Flask(__name__, static_folder=imagesPath, static_url_path='/static')
        self.host = host
        self.port = port
        self.game = game

        self.blockList = self.game.getObjectList('block')
        
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
        event = threading.Event()
        def resolve():
            event.set()
        self.pending_requests.append(resolve)
        event.wait(timeout=30.0)
        if resolve in self.pending_requests:
            self.pending_requests.remove(resolve)
        return jsonify({"status": "ok"})

    def getFullMapJson(self):
        mapViewJs = self.game.getMapPart(0, 0, data.worldSize, data.worldSize)
        fullMap = []
        for row in mapViewJs:
            webRow = []
            for cell in row:
                blockId = inventory.getBlockTypeId(cell['block'])
                webRow.append({
                    "g": blockId,
                    "zone": cell["zone"]
                })
            fullMap.append(webRow)
        return jsonify({
            "map": fullMap,
            "maxSize": data.worldSize,
            "spawnPos": data.spawnPos
        })
        
    def getEntitiesJson(self):
        entitiesList = []
        entities = self.game.getEntitiesList()
        for ent in entities:
            eDir = inventory.getDir(ent)
            entityType = ent.__class__.__name__.lower()
            entityName = inventory.getName(ent)
            def serializeItem(item):
                if not item or item == 'None':
                    return None
                boosts = self.game.getValue('boosts', ['name', item]) or {}
                return {"name": item, "boosts": boosts}
            entitiesList.append({
                "id": inventory.getMyId(ent),
                "name": entityName,
                "asset": entityName if entityType == 'player' else f"{inventory.getTypeId(ent)}{eDir}",
                "type": entityType,
                "hp": inventory.getHealth(ent),
                "dir": eDir,
                "equipped": [[slot, itm] for slot, itm in inventory.getEquipped(ent).items()],
                "inventory": [serializeItem(itm) for itm in inventory.getInventory(ent)],
                "x": float(ent.x),
                "y": float(ent.y),
                "speed": inventory.getSpeed(ent),
                "sight": int(inventory.getSight(ent)),
                "lastSkinUpdate": getattr(ent, 'lastSkinUpdate', 0)
            })
        return jsonify(entitiesList)

    def getDocumentationText(self):
        doc_path = os.path.join(os.path.dirname(__file__), data.documentName)
        if os.path.exists(doc_path):
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return "error when reading file"
        return "file not found"

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
                .player-item { display: flex; justify-content: flex-start; align-items: center; margin-bottom: 8px; background: rgba(255, 255, 255, 0.08); padding: 10px 14px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08); width: 100%; color: #fff; font-weight: bold; font-size: 14px; text-align: left; cursor: pointer; transition: background 120ms ease, transform 120ms ease; touch-action: manipulation; }
                .player-item:hover { background: rgba(76, 175, 80, 0.18); }
                .player-item:active { background: rgba(76, 175, 80, 0.28); transform: translateY(1px); }

                #infoPanel { 
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    z-index: 10;
                    background: rgba(30, 30, 30, 0.92);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 12px;
                    padding: 16px;
                    width: 280px;
                    max-height: calc(100% - 30px);
                    overflow-y: auto;
                    text-align: left;
                    font-size: 14px;
                    box-shadow: 0px 6px 20px rgba(0,0,0,0.24);
                    backdrop-filter: blur(8px);
                }
                #infoPanel h3 { margin: 0 0 10px 0; color: #4CAF50; font-size: 16px; border-bottom: 1px solid #555; padding-bottom: 5px; }
                .info-row { display: flex; flex-direction: column; margin-bottom: 8px; }
                .info-row-inline { display: flex; justify-content: space-between; margin-bottom: 5px; }
                .info-label { color: #aaa; font-weight: bold; margin-bottom: 2px; }
                .info-value { color: #fff; word-break: break-word; line-height: 1.4; }
                .info-section { margin-bottom: 14px; }
                .info-section .info-label { margin-bottom: 6px; }
                .info-section.inventory,
                .info-section.equipped { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 8px 10px; }
                .info-section.inventory .info-label,
                .info-section.equipped .info-label { color: #cccccc; font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; }
                .info-section.inventory .info-value,
                .info-section.equipped .info-value { margin-top: 4px; }
                .inventory-grid,
                .equipped-grid { display: grid; grid-template-columns: 1fr; gap: 2px; margin-top: 4px; }
                .item-box { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 6px 8px; box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03); }
                
                .detail-box { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; margin-bottom: 8px; }
                .detail-box .info-label { margin-bottom: 0; }
                
                .item-name { font-weight: bold; color: #f0f0f0; margin-bottom: 4px; font-size: 13px; }
                .item-subtext { color: #b4b4b4; font-size: 12px; margin-bottom: 4px; }
                .item-boosts { color: #c8ffc8; font-size: 12px; margin-left: 4px; line-height: 1.2; }
                .item-boosts div { margin-bottom: 3px; }
                .boost-key { color: #b2ffb2; font-weight: 600; }
                .boost-value { color: #e8f5e9; font-weight: 700; }
                .hidden { display: none !important; }
                
                #docBtn {
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    z-index: 9999;
                    padding: 4px 8px;
                    font-size: 11px;
                    background-color: #2c3e50;
                    color: #ffffff;
                    border: 1px solid #455a64;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: 600;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
                    transition: background-color 0.2s;
                }

                #docBtn:hover {
                    background-color: #37474f;
                }

                .doc-modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    z-index: 10000;
                    backdrop-filter: blur(2px);
                }

                .doc-modal-content {
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                    width: 65%;
                    max-width: 800px;
                    max-height: 80vh;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #444;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
                    overflow-y: auto;
                    font-family: monospace;
                }

                .doc-modal-content pre {
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-family: inherit;
                    font-size: 13px;
                    line-height: 1.5;
                    margin: 0;
                    color: #dcdcdc;
                }
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
                    
                    <div id="hpRow" class="info-row-inline item-box detail-box"><span class="info-label">HP:</span><span class="info-value" id="infoHp">N/A</span></div>
                    
                    <div id="zoneRow" class="info-row-inline item-box detail-box"><span class="info-label">Zone:</span><span class="info-value" id="infoZone">N/A</span></div>
                    
                    <div id="statsContainer">
                        <div class="info-row info-section equipped" id="equippedRow">
                            <span class="info-label">Equipped</span>
                            <div class="info-value" id="infoEquipped"></div>
                        </div>
                        <div class="info-row info-section inventory" id="inventoryRow">
                            <span class="info-label">Inventory</span>
                            <div class="info-value" id="infoInventory"></div>
                        </div>
                    </div>
                </div>

                <button id="docBtn" onclick="openDocModal()">Documentation</button>

                <div id="docModal" class="doc-modal-overlay" style="display: none;" onclick="closeDocModal(event)">
                    <div class="doc-modal-content" onclick="event.stopPropagation()">
                        <pre id="docText">{{ docContent }}</pre>
                    </div>
                </div>
            </div>

            <script>
                function formatWebPath(rawPath) {
                    let p = rawPath.replace("serverHTML/static/", "static/");
                    if (!p.startsWith("/")) p = "/" + p;
                    if (!p.endsWith("/")) p = p + "/";
                    return p;
                }

                const imagesBasePath = formatWebPath("{{ imagesFilePath }}");
                const playerImagePath = imagesBasePath;
                const entitiesImagePath = imagesBasePath;
                const blocksImagePath = imagesBasePath;

                const canvas = document.getElementById('gameCanvas'); 
                const canvasContainer = document.getElementById('canvasContainer');
                const ctx = canvas.getContext('2d');
                
                const baseBlockSize = 40; 
                let zoomLevel = 2.0;
                const minZoom = 0.4;
                const maxZoom = 4.0;
                
                let cameraC = 0.0; 
                let cameraR = 0.0; 
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

                const assetsToLoad = ["26", "10", "10north"];
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
                    img.src = `${blocksImagePath}${assetName}.png`;
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

                function loadAndRegisterAsset(assetName, type, forceReload = false, cacheTimestamp = null) {
                    let path = (type === 'player') ? playerImagePath : entitiesImagePath;
                    
                    const cacheBusterTime = cacheTimestamp !== null ? cacheTimestamp : Date.now();

                    if (textures[assetName] === undefined || (type === 'player' && forceReload)) {
                        if (textures[assetName] === undefined) {
                            textures[assetName] = "loading"; 
                        }
                        const img = new Image();
                        const cacheBuster = (type === 'player') ? `?t=${cacheBusterTime}` : '';
                        img.src = `${path}${assetName}.png${cacheBuster}`;
                        img.onload = () => { textures[assetName] = img; };
                        img.onerror = () => { 
                            if (!textures[assetName] || textures[assetName] === "loading") {
                                textures[assetName] = null; 
                            }
                        };
                    }

                    const baseAsset = assetName.replace(/(north|south|east|west)/g, '');
                    if (baseAsset !== assetName && (textures[baseAsset] === undefined || (type === 'player' && forceReload))) {
                        const baseImg = new Image();
                        const cacheBuster = (type === 'player') ? `?t=${cacheBusterTime}` : '';
                        baseImg.src = `${path}${baseAsset}.png${cacheBuster}`;
                        baseImg.onload = () => { textures[baseAsset] = baseImg; };
                        baseImg.onerror = () => { 
                            if (!textures[baseAsset] || textures[baseAsset] === "loading") {
                                textures[baseAsset] = null; 
                            }
                        };
                    }
                }

                function loadEntireWorld() {
                    fetch('/api/fullMap')
                        .then(res => {
                            if (!res.ok) throw new Error("Server restarting...");
                            return res.json();
                        })
                        .then(data => {
                            currentEntities = [];
                            for (let member in discoveredTiles) delete discoveredTiles[member];
                            currentlyVisibleTiles.clear();

                            fullWorldMap = data.map;
                            maxWorldSize = data.maxSize;
                            zoomLevel = 2.0;
                            
                            if (data.spawnPos && data.spawnPos.length === 2) {
                                centerCameraOn(data.spawnPos[0], data.spawnPos[1]);
                            } else {
                                centerCameraOn(50, 75);
                            }

                            loadEntitiesOnly();
                            requestAnimationFrame(startRenderLoop);
                            startPollingLoop();
                        })
                        .catch(() => {
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
                                
                                let needsSkinUpdate = false;

                                if (existing) {
                                    existing.targetX = Number(nEnt.x);
                                    existing.targetY = Number(nEnt.y);
                                    existing.speed = Number(nEnt.speed) || 5.0;
                                    existing.asset = nEnt.asset;
                                    existing.hp = nEnt.hp;
                                    existing.equipped = nEnt.equipped;
                                    existing.inventory = nEnt.inventory;
                                    existing.sight = nEnt.sight;
                                    existing.type = nEnt.type;
                                    existing.name = nEnt.name;
                                    existing.dir = nEnt.dir;
                                    
                                    if (existing.lastSkinUpdate !== nEnt.lastSkinUpdate) {
                                        needsSkinUpdate = true;
                                        existing.lastSkinUpdate = nEnt.lastSkinUpdate;
                                    }
                                } else {
                                    nEnt.targetX = Number(nEnt.x);
                                    nEnt.targetY = Number(nEnt.y);
                                    nEnt.x = nEnt.targetX; 
                                    nEnt.y = nEnt.targetY;
                                    nEnt.speed = Number(nEnt.speed) || 5.0;
                                    nEnt.lastSkinUpdate = nEnt.lastSkinUpdate || 0;
                                    
                                    needsSkinUpdate = true;
                                    currentEntities.push(nEnt);
                                }
                                
                                loadAndRegisterAsset(nEnt.asset, nEnt.type, needsSkinUpdate, nEnt.lastSkinUpdate);
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
                        container.innerHTML = '<div style="color: #aaa; font-style: italic; font-size: 13px;">No players</div>';
                        return;
                    }

                    function openPlayerPanel(player) {
                        teleportToPlayer(player.id);
                        selectedEntity = player.id;
                        showEntityDetails(player);
                    }

                    players.forEach(p => {
                        const item = document.createElement('button');
                        item.type = 'button';
                        item.className = 'player-item';
                        item.innerText = p.name || `Player ${p.id}`;

                        item.addEventListener('pointerdown', (e) => {
                            e.preventDefault();
                            openPlayerPanel(p);
                        });

                        item.addEventListener('click', (e) => {
                            e.preventDefault();
                            openPlayerPanel(p);
                        });

                        container.appendChild(item);
                    });
                }

                function centerCameraOn(x, y) {
                    const drawSize = baseBlockSize * zoomLevel;
                    const visibleCols = canvas.width / drawSize;
                    const visibleRows = canvas.height / drawSize;

                    cameraC = Math.max(0, Math.min((x + 0.5) - (visibleCols / 2), maxWorldSize - 1));
                    cameraR = Math.max(0, Math.min((y + 0.5) - (visibleRows / 2), maxWorldSize - 1));
                }

                function teleportToPlayer(playerId) {
                    followedPlayerId = playerId;
                    const p = currentEntities.find(e => e.id === playerId);
                    if (p) {
                        zoomLevel = 2.0;
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
                    if (!nowTime) nowTime = performance.now();
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
                        if (ent.type === "player" && ent.dir) {
                            ctx.save();
                            
                            ctx.translate(posX + drawSize / 2, posY + drawSize / 2);
                            
                            let angle = 0;
                            if (ent.dir === 'east') angle = Math.PI / 2;
                            else if (ent.dir === 'south') angle = Math.PI;
                            else if (ent.dir === 'west') angle = 3 * Math.PI / 2;
                            
                            ctx.rotate(angle);
                            
                            ctx.drawImage(img, -drawSize / 2, -drawSize / 2, drawSize, drawSize);
                            
                            ctx.restore();
                        } else {
                            ctx.drawImage(img, posX, posY, drawSize, drawSize);
                        }
                    } else {
                        ctx.beginPath();
                        ctx.arc(posX + drawSize / 2, posY + drawSize / 2, drawSize * 0.4, 0, 2 * Math.PI);
                        
                        if (ent.type === "player") ctx.fillStyle = "#4CAF50";
                        else if (ent.type === "chest") ctx.fillStyle = "#FFC107";
                        else ctx.fillStyle = "#F44336";
                        
                        ctx.fill();
                        ctx.lineWidth = 2;
                        ctx.strokeStyle = "#FFFFFF";
                        ctx.stroke();
                    }
                }

                function updateEntityPositions(dt) {
                    currentEntities.forEach(ent => {
                        if (ent.targetX !== undefined && ent.targetY !== undefined) {
                            const dx = ent.targetX - ent.x;
                            const dy = ent.targetY - ent.y;
                            const dist = Math.sqrt(dx * dx + dy * dy);

                            if (dist > 1.5) {
                                ent.x = ent.targetX;
                                ent.y = ent.targetY;
                            } else if (dist > 0.01) {
                                const moveDist = ent.speed * dt;
                                if (moveDist >= dist) {
                                    ent.x = ent.targetX;
                                    ent.y = ent.targetY;
                                } else {
                                    ent.x += (dx / dist) * moveDist;
                                    ent.y += (dy / dist) * moveDist;
                                }
                            } else {
                                ent.x = ent.targetX;
                                ent.y = ent.targetY;
                            }
                        }
                    });
                }

                function renderMap(dt) {
                    updateEntityPositions(dt);

                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    const drawSize = baseBlockSize * zoomLevel;

                    if (followedPlayerId !== null && !isDragging) {
                        const fPlayer = currentEntities.find(e => e.id === followedPlayerId);
                        if (fPlayer) {
                            centerCameraOn(fPlayer.x, fPlayer.y);
                        }
                    }

                    const startCol = Math.max(0, Math.floor(cameraC));
                    const startRow = Math.max(0, Math.floor(cameraR));
                    const endCol = Math.min(maxWorldSize, startCol + Math.ceil(canvas.width / drawSize) + 1);
                    const endRow = Math.min(maxWorldSize, startRow + Math.ceil(canvas.height / drawSize) + 1);

                    const now = Date.now();

                    for (let r = startRow; r < endRow; r++) {
                        for (let c = startCol; c < endCol; c++) {
                            const posX = (c - cameraC) * drawSize;
                            const posY = (r - cameraR) * drawSize;
                            const key = `${c},${r}`;

                            const inPlayerSight = currentlyVisibleTiles.has(key);
                            const lastSeenTime = discoveredTiles[key] || 0;
                            const isVisible = inPlayerSight || (now - lastSeenTime <= fogRevealTimeoutMs);

                            if (isVisible) {
                                if (fullWorldMap[r] && fullWorldMap[r][c]) {
                                    const cell = fullWorldMap[r][c];
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

                        if (posX + drawSize >= 0 && posY + drawSize >= 0 && posX <= canvas.width && posY <= canvas.height) {
                            if (ent.type === "player") {
                                drawAnimatedEntity(ent, posX, posY, drawSize);
                            } else {
                                const entX = Math.round(ent.x);
                                const entY = Math.round(ent.y);
                                const key = `${entX},${entY}`;
                                
                                const inSight = currentlyVisibleTiles.has(key);
                                const seenRecent = (now - (discoveredTiles[key] || 0) <= fogRevealTimeoutMs);

                                if (inSight || seenRecent) {
                                    drawAnimatedEntity(ent, posX, posY, drawSize);
                                }
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
                    
                    const clickWorldFloatX = cameraC + (clickX / drawSize);
                    const clickWorldFloatY = cameraR + (clickY / drawSize);
                    
                    const clickedEntity = currentEntities.find(ent => {
                        return clickWorldFloatX >= ent.x && clickWorldFloatX <= (ent.x + 1.0) &&
                               clickWorldFloatY >= ent.y && clickWorldFloatY <= (ent.y + 1.0);
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
                    const hpRow = document.getElementById('hpRow');
                    const zoneRow = document.getElementById('zoneRow');
                    const equippedRow = document.getElementById('equippedRow');
                    const inventoryRow = document.getElementById('inventoryRow');
                    const infoTitle = document.getElementById('infoTitle');

                    if (ent.hp !== undefined && ent.hp !== null) {
                        document.getElementById('infoHp').innerText = ent.hp;
                    } else {
                        document.getElementById('infoHp').innerText = 'N/A';
                    }

                    const entType = String(ent.type || '');

                    function renderInventory() {
                        let invItems = [];
                        if (ent.inventory) {
                            if (Array.isArray(ent.inventory)) {
                                invItems = ent.inventory.filter(item => item !== null && item !== undefined && item !== 'None' && item !== '');
                            } else if (typeof ent.inventory === 'object') {
                                invItems = Object.values(ent.inventory).filter(item => item !== null && item !== undefined && item !== 'None' && item !== '');
                            }
                        }

                        if (invItems.length === 0) {
                            document.getElementById('infoInventory').innerHTML = '<span style="color: #888;"></span>';
                            return;
                        }

                        const inventoryHtml = invItems.map(item => {
                            const itemName = (typeof item === 'string') ? item : (item.name || 'Unknown');
                            let boostsHtml = '';
                            const boosts = (item && typeof item === 'object') ? item.boosts : null;
                            const bodySlot = (item && typeof item === 'object' && Array.isArray(item.bodySlot) && item.bodySlot.length > 0)
                                ? `<div class="item-subtext">${item.bodySlot.join(', ')}</div>`
                                : '';

                            if (boosts && typeof boosts === 'object' && Object.keys(boosts).length > 0) {
                                boostsHtml = '<div class="item-boosts">' + Object.entries(boosts)
                                    .map(([key, value]) => {
                                        const displayValue = Number(value) > 0 ? `+${value}` : value;
                                        return `<div><span class="boost-key">${key}</span>: <span class="boost-value">${displayValue}</span></div>`;
                                    })
                                    .join('') + '</div>';
                            }

                            return `<div class="item-box"><div class="item-name">${itemName}</div>${bodySlot}${boostsHtml}</div>`;
                        }).join('');

                        document.getElementById('infoInventory').innerHTML = `<div class="inventory-grid">${inventoryHtml}</div>`;
                    }

                    function renderEquipped() {
                        let equippedItems = [];
                        if (ent.equipped) {
                            if (Array.isArray(ent.equipped)) {
                                equippedItems = ent.equipped.map(([slot, item]) => [slot, item]);
                            } else if (typeof ent.equipped === 'object') {
                                equippedItems = Object.entries(ent.equipped);
                            }
                        }

                        if (equippedItems.length === 0) {
                            document.getElementById('infoEquipped').innerHTML = '<span style="color: #888;"></span>';
                            return;
                        }

                        const equippedHtml = equippedItems.map(([slot, item]) => {
                            const itemName = (item === null || item === undefined || item === 'None' || item === '')
                                ? ' '
                                : ((typeof item === 'string') ? item : (item.name || 'Unknown'));
                            const bodySlot = (item && typeof item === 'object' && Array.isArray(item.bodySlot) && item.bodySlot.length > 0)
                                ? `<div class="item-subtext">${item.bodySlot.join(', ')}</div>`
                                : '';
                            let boostsHtml = '';
                            const boosts = (item && typeof item === 'object') ? item.boosts : null;
                            if (boosts && typeof boosts === 'object' && Object.keys(boosts).length > 0) {
                                boostsHtml = '<div class="item-boosts">' + Object.entries(boosts)
                                    .map(([key, value]) => {
                                        const displayValue = Number(value) > 0 ? `+${value}` : value;
                                        return `<div><span class="boost-key">${key}</span>: <span class="boost-value">${displayValue}</span></div>`;
                                    })
                                    .join('') + '</div>';
                            }
                            const title = itemName ? `${slot}: ${itemName}` : slot;
                            return `<div class="item-box"><div class="item-name">${title}</div>${bodySlot}${boostsHtml}</div>`;
                        }).join('');

                        document.getElementById('infoEquipped').innerHTML = `<div class="equipped-grid">${equippedHtml}</div>`;
                    }

                    if (entType === 'player') {
                        infoTitle.innerText = ent.name || `Player ${ent.id}`;
                        hpRow.classList.remove('hidden');
                        zoneRow.classList.add('hidden');
                        equippedRow.classList.remove('hidden');
                        inventoryRow.classList.remove('hidden');

                        renderEquipped();
                        renderInventory();

                    } else if (entType === 'grave') {
                        infoTitle.innerText = "Grave";
                        hpRow.classList.add('hidden');
                        zoneRow.classList.add('hidden');
                        equippedRow.classList.add('hidden');
                        inventoryRow.classList.remove('hidden');
                        renderInventory();

                    } else if (entType === 'chest') {
                        infoTitle.innerText = "Chest";
                        hpRow.classList.add('hidden');
                        equippedRow.classList.add('hidden');
                        inventoryRow.classList.add('hidden');
                        zoneRow.classList.remove('hidden');

                        const ex = Math.round(ent.x);
                        const ey = Math.round(ent.y);
                        let zoneName = "UNKNOWN";
                        if (fullWorldMap[ey] && fullWorldMap[ey][ex]) {
                            zoneName = fullWorldMap[ey][ex].zone || "UNKNOWN";
                        }
                        document.getElementById('infoZone').innerText = zoneName.toUpperCase();

                    } else if (entType === 'enemy') {
                        infoTitle.innerText = "Enemy";
                        hpRow.classList.remove('hidden');
                        zoneRow.classList.remove('hidden');
                        equippedRow.classList.add('hidden');
                        inventoryRow.classList.add('hidden');

                        const ex = Math.round(ent.x);
                        const ey = Math.round(ent.y);
                        let zoneName = "UNKNOWN";
                        if (fullWorldMap[ey] && fullWorldMap[ey][ex]) {
                            zoneName = fullWorldMap[ey][ex].zone || "UNKNOWN";
                        }
                        document.getElementById('infoZone').innerText = zoneName.toUpperCase();

                    } else {
                        infoTitle.innerText = "Entity";
                        hpRow.classList.remove('hidden');
                        zoneRow.classList.remove('hidden');
                        equippedRow.classList.add('hidden');
                        inventoryRow.classList.add('hidden');
                        
                        const ex = Math.round(ent.x);
                        const ey = Math.round(ent.y);
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
                
                function openDocModal() {
                    document.getElementById('docModal').style.display = 'flex';
                }

                function closeDocModal(event) {
                    if (event.target.id === 'docModal') {
                        document.getElementById('docModal').style.display = 'none';
                    }
                }
            </script>
        </body>
        </html>
        """
        return render_template_string(htmlCode, 
                          blocksBackend=self.blockList, 
                          docContent=self.getDocumentationText(),
                          imagesFilePath=data.imagesFilePath)
    
    def startServer(self):
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)