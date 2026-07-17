import os
from flask import Flask, jsonify, request, render_template_string

class ServerHTML:
    def __init__(self, host, port, getMapPart, worldSize, blockList):
        imagesPath = os.path.join(os.path.dirname(__file__), 'static')
        
        self.app = Flask(__name__, static_folder=imagesPath, static_url_path='/static')
        self.host = host
        self.port = port
        
        self.getMapPart = getMapPart
        self.worldSize = worldSize
        self.blockList = blockList
        
        self.pending_requests = []

        self.app.add_url_rule("/", "index", self.website)
        self.app.add_url_rule("/api/mapView", "mapView", self.getMapViewJson)
        self.app.add_url_rule("/api/entities", "entities", self.getEntitiesJson)
        self.app.add_url_rule("/api/pollEntities", "pollEntities", self.pollEntities)

    def updateEntities(self):
        """Zavolaj z hry pre okamžitý update pozícií entít."""
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

    def getMapViewJson(self):
        """Endpoint pre bloky terénu."""
        startY = int(request.args.get("r", 0))
        startX = int(request.args.get("c", 0))
        width = int(request.args.get("w", 40))
        height = int(request.args.get("h", 20))

        mapViewJs = self.getMapPart(startX, startY, width, height)

        webMap = []
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
            webMap.append(webRow)

        return jsonify({
            "map": webMap,
            "startX": startX,
            "startY": startY,
            "maxSize": self.worldSize
        })

    def getEntitiesJson(self):
        """Endpoint pre dynamické entity."""
        startY = int(request.args.get("r", 0))
        startX = int(request.args.get("c", 0))
        width = int(request.args.get("w", 40))
        height = int(request.args.get("h", 20))

        mapViewJs = self.getMapPart(startX, startY, width, height)

        entitiesList = []
        for r in range(len(mapViewJs)):
            for c in range(len(mapViewJs[r])):
                cell = mapViewJs[r][c]
                if cell and cell.get('entities'):
                    entities = cell['entities']
                    if isinstance(entities, dict):
                        for instanceId, entityObj in entities.items():
                            if entityObj:
                                drawId = None
                                eType = "Unknown"
                                eHp = "N/A"
                                eDir = "north"
                                eX = startX + c
                                eY = startY + r
                                
                                if isinstance(entityObj, dict):
                                    drawId = entityObj.get("entity", {}).get("id") if isinstance(entityObj.get("entity"), dict) else entityObj.get("id")
                                    eType = entityObj.get("entity", {}).get("name", "Unknown") if isinstance(entityObj.get("entity"), dict) else entityObj.get("type", "Unknown")
                                    eHp = entityObj.get("hp", "N/A")
                                    eDir = entityObj.get("dir", "north")
                                    eX = entityObj.get("x", eX)
                                    eY = entityObj.get("y", eY)
                                else:
                                    if hasattr(entityObj, "entity") and isinstance(entityObj.entity, dict):
                                        drawId = entityObj.entity.get("id")
                                        eType = entityObj.entity.get("name", "Unknown")
                                    else:
                                        drawId = getattr(entityObj, "entityId", None)
                                    eHp = getattr(entityObj, "hp", "N/A")
                                    eDir = getattr(entityObj, "dir", "north")
                                    eX = getattr(entityObj, "x", eX)
                                    eY = getattr(entityObj, "y", eY)
                                
                                if drawId is not None:
                                    entitiesList.append({
                                        "id": drawId,
                                        "asset": f"{drawId}{eDir}",
                                        "type": eType,
                                        "hp": eHp,
                                        "x": float(eX),
                                        "y": float(eY),
                                        "zone": cell.get("zone", "unknown")
                                    })
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
                
                const terrainCache = {};
                let currentEntities = [];
                
                let mapStartX = 0;
                let mapStartY = 0;
                let mapWidth = 0;
                let mapHeight = 0;
                
                let selectedEntity = null;
                
                let isDragging = false;
                let startX, startY;
                let startCameraC, startCameraR;
                let totalDragDistance = 0; // Sleduje, či sme s myšou pohli, alebo len klikli

                canvas.width = visibleColumns * baseBlockSize; 
                canvas.height = visibleRows * baseBlockSize;

                const blocksConfig = {{ blocksBackend | tojson }};
                const textures = {};
                let loadedImagesCount = 0;

                const assetsToLoad = [];
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
                            loadMapChunk();
                            startPollingLoop();
                        }
                    };
                    img.onerror = function() {
                        loadedImagesCount++;
                        if (loadedImagesCount === totalAssetsCount) {
                            loadMapChunk();
                            startPollingLoop();
                        }
                    };
                    textures[assetName] = img;
                });

                function loadAndRegisterAsset(assetName) {
                    if (textures[assetName]) return;
                    const img = new Image();
                    img.src = `/static/${assetName}.png`;
                    img.onload = () => { textures[assetName] = img; requestAnimationFrame(renderMap); };
                    img.onerror = () => { textures[assetName] = null; };
                    textures[assetName] = img;
                }

                function loadMapChunk() {
                    const colsToFetch = Math.ceil(visibleColumns / zoomLevel);
                    const rowsToFetch = Math.ceil(visibleRows / zoomLevel);
                    
                    const buffer = 5;
                    const fetchX = Math.max(0, Math.floor(cameraC) - buffer);
                    const fetchY = Math.max(0, Math.floor(cameraR) - buffer);
                    mapWidth = colsToFetch + (buffer * 2);
                    mapHeight = rowsToFetch + (buffer * 2);
                    
                    mapStartX = fetchX;
                    mapStartY = fetchY;

                    let missingBlocks = false;
                    for (let r = 0; r < mapHeight; r++) {
                        for (let c = 0; c < mapWidth; c++) {
                            const wx = mapStartX + c;
                            const wy = mapStartY + r;
                            if (wx >= 0 && wx < maxWorldSize && wy >= 0 && wy < maxWorldSize) {
                                if (terrainCache[`${wx},${wy}`] === undefined) {
                                    missingBlocks = true;
                                    break;
                                }
                            }
                        }
                        if (missingBlocks) break;
                    }

                    if (missingBlocks) {
                        fetch(`/api/mapView?r=${mapStartY}&c=${mapStartX}&w=${mapWidth}&h=${mapHeight}`)
                            .then(res => res.json())
                            .then(data => {
                                for (let r = 0; r < data.map.length; r++) {
                                    for (let c = 0; c < data.map[r].length; c++) {
                                        const wx = data.startX + c;
                                        const wy = data.startY + r;
                                        terrainCache[`${wx},${wy}`] = data.map[r][c];
                                    }
                                }
                                loadEntitiesOnly();
                            });
                    } else {
                        loadEntitiesOnly();
                    }
                }

                function loadEntitiesOnly() {
                    if (mapWidth === 0 || mapHeight === 0) return;
                    
                    fetch(`/api/entities?r=${mapStartY}&c=${mapStartX}&w=${mapWidth}&h=${mapHeight}`)
                        .then(res => res.json())
                        .then(entities => {
                            currentEntities = entities;
                            
                            currentEntities.forEach(ent => {
                                loadAndRegisterAsset(ent.asset);
                            });
                            
                            updateInfoPanel();
                            requestAnimationFrame(renderMap);
                        });
                }

                function startPollingLoop() {
                    fetch('/api/pollEntities')
                        .then(res => res.json())
                        .then(() => {
                            // ODSTRÁNENÁ podmienka !isDragging -> entity sa updatujú neustále
                            loadEntitiesOnly();
                            startPollingLoop();
                        })
                        .catch(() => {
                            setTimeout(startPollingLoop, 1000);
                        });
                }

                function renderMap() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    const drawSize = baseBlockSize * zoomLevel;

                    const colsToDraw = Math.ceil(canvas.width / drawSize) + 2;
                    const rowsToDraw = Math.ceil(canvas.height / drawSize) + 2;
                    
                    const startDrawX = Math.floor(cameraC);
                    const startDrawY = Math.floor(cameraR);

                    for (let r = -1; r < rowsToDraw; r++) {
                        for (let c = -1; c < colsToDraw; c++) {
                            const wx = startDrawX + c;
                            const wy = startDrawY + r;
                            
                            if (wx < 0 || wx >= maxWorldSize || wy < 0 || wy >= maxWorldSize) {
                                continue;
                            }
                            
                            const posX = (wx - cameraC) * drawSize;
                            const posY = (wy - cameraR) * drawSize;

                            // 1. KONTROLA, ČI POLÍČKO VIDÍ NEJAKÝ HRÁČ
                            let isVisible = false;

                            for (let i = 0; i < currentEntities.length; i++) {
                                const ent = currentEntities[i];
                                
                                // Hmlu odkrýva LEN entita, ktorej typ je 'player' (prípadne 'Player')
                                if (ent.type && ent.type.toLowerCase() === 'player') {
                                    const sight = ent.sight || 5; // Ak hráč nemá sight z backendu, nastavíme mu napr. 5

                                    if (Math.abs(ent.x - wx) <= sight && Math.abs(ent.y - wy) <= sight) {
                                        isVisible = true;
                                        break; // Našli sme hráča, čo sem vidí, netreba hľadať ďalej
                                    }
                                }
                            }

                            // 2. VYKRESLENIE TERÉNU ALEBO OBLAKU
                            if (isVisible) {
                                const cell = terrainCache[`${wx},${wy}`];
                                if (cell && cell.g !== null && textures[cell.g]) {
                                    ctx.drawImage(textures[cell.g], posX, posY, drawSize, drawSize);
                                }
                            } else {
                                // Políčko je v tme -> oblak
                                if (textures["26"]) {
                                    ctx.drawImage(textures["26"], posX, posY, drawSize, drawSize);
                                } else {
                                    ctx.fillStyle = "#444";
                                    ctx.fillRect(posX, posY, drawSize, drawSize);
                                }
                            }
                        }
                    }

                    // 3. VYKRESLENIE ENTÍT (Zobrazia sa len tie, ktoré sú odkrívené svetlom hráča)
                    currentEntities.forEach(ent => {
                        const posX = (ent.x - cameraC) * drawSize;
                        const posY = (ent.y - cameraR) * drawSize;

                        if (posX + drawSize < 0 || posY + drawSize < 0 || posX > canvas.width || posY > canvas.height) {
                            return;
                        }

                        // AK CHCEŠ, ABY POTVORY V OBLAKOCH BOLI SKRYTÉ:
                        // Skontrolujeme, či pozícia potvory leží vo viditeľnej zóne nejakého hráča
                        let entVisible = (ent.type && ent.type.toLowerCase() === 'player'); // Hráč vidí sám seba vždy
                        
                        if (!entVisible) {
                            for (let i = 0; i < currentEntities.length; i++) {
                                const p = currentEntities[i];
                                if (p.type && p.type.toLowerCase() === 'player') {
                                    const pSight = p.sight || 5;
                                    if (Math.abs(p.x - ent.x) <= pSight && Math.abs(p.y - ent.y) <= pSight) {
                                        entVisible = true;
                                        break;
                                    }
                                }
                            }
                        }

                        // Vykreslíme entitu iba ak je viditeľná (alebo ak chceš vidieť potvory aj v hmle, podmienku 'if (entVisible)' vymaž)
                        if (entVisible && textures[ent.asset]) {
                            ctx.drawImage(textures[ent.asset], posX, posY, drawSize, drawSize);
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

                // ZMENA NA ĽAVÉ TLAČIDLO (mousedown)
                canvas.addEventListener('mousedown', function(e) {
                    if (e.button === 0) { // 0 = Ľavé tlačidlo
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
                    
                    requestAnimationFrame(renderMap);
                });

                // ZMENA NA ĽAVÉ TLAČIDLO (mouseup)
                window.addEventListener('mouseup', function(e) {
                    if (e.button === 0 && isDragging) {
                        isDragging = false;
                        
                        // Ak sme myšou takmer nepohli, berieme to ako obyčajné kliknutie (výber entity)
                        if (totalDragDistance < 5) {
                            handleCanvasClick(e);
                        } else {
                            // Ak sme mapu reálne ťahali, len načítame nové chunk bloky na pozadí
                            loadMapChunk();
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
                    
                    if (zoomLevel === previousZoom) {
                        return;
                    }
                    
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    const gridXBefore = cameraC + (mouseX / (baseBlockSize * previousZoom));
                    const gridYBefore = cameraR + (mouseY / (baseBlockSize * previousZoom));
                    
                    const maxC = maxWorldSize - (visibleColumns / zoomLevel);
                    const maxR = maxWorldSize - (visibleRows / zoomLevel);
                    
                    cameraC = Math.max(0, Math.min(gridXBefore - (mouseX / (baseBlockSize * zoomLevel)), maxC));
                    cameraR = Math.max(0, Math.min(gridYBefore - (mouseY / (baseBlockSize * zoomLevel)), maxR));

                    loadMapChunk(); 
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
                    document.getElementById('infoZone').innerText = ent.zone.toUpperCase();
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
                    loadMapChunk();
                }
            </script>
        </body>
        </html>
        """
        return render_template_string(htmlCode, blocksBackend=self.blockList)
    
    def startServer(self):
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)