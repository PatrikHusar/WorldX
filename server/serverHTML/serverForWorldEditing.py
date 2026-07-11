import os
from flask import Flask, jsonify, request, render_template_string

class ServerHTML:
    def __init__(self, host, port, getMapPart, blockChange, worldSize, blockList):
        imagesPath = os.path.join(os.path.dirname(__file__), 'static')
        
        self.app = Flask(__name__, static_folder=imagesPath, static_url_path='/static')
        self.host = host
        self.port = port
        
        self.getMapPart = getMapPart
        self.blockChange = blockChange
        self.worldSize = worldSize
        self.blockList = blockList

        self.app.add_url_rule("/", "index", self.website)
        self.app.add_url_rule("/api/mapView", "mapView", self.getMapViewJson)
        self.app.add_url_rule("/api/blockChange", "blockChange", self.updateBlockOnMap, methods=["POST"])

    def getMapViewJson(self):
        startY = int(request.args.get("r", 0))
        startX = int(request.args.get("c", 0))
        width = int(request.args.get("w", 40))
        height = int(request.args.get("h", 20))

        mapViewJs = self.getMapPart(startX, startY, width, height)

        return jsonify({
            "map": mapViewJs,
            "startX": startX,
            "startY": startY,
            "maxSize": self.worldSize
        })

    def updateBlockOnMap(self):
        data = request.json
        x = data.get("x")
        y = data.get("y")
        newId = data.get("newId")

        if self.blockChange(x, y, newId):
            return jsonify({"status": "ok"})
        return jsonify({"status": "error"}), 400

    def website(self):
        htmlCode = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WorldX Editor</title>
            <style>
                body { font-family: Arial, sans-serif; background: #222; color: white; text-align: center; margin: 0; padding: 5px 10px; user-select: none; overflow-y: hidden; }
                h1 { margin-top: 5px; margin-bottom: 5px; font-size: 24px; }
                .control-panel { display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 5px; }
                #coordinates { font-weight: bold; color: #4CAF50; font-size: 16px; }
                .teleport-container input { padding: 6px; font-size: 13px; border: 1px solid #666; border-radius: 4px; background: #333; color: white; text-align: center; width: 120px; }
                .teleport-container button { padding: 6px 12px; font-size: 13px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px; font-weight: bold; }
                .teleport-container button:hover { background: #45a049; }
                
                .game-container { display: flex; justify-content: center; align-items: flex-start; gap: 15px; max-width: 1700px; margin: 0 auto; }
                #gameCanvas { border: 4px solid #555; background: #000; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
                
                .sidebar { background: #333; border: 4px solid #555; border-radius: 4px; padding: 10px; display: flex; flex-direction: column; gap: 10px; min-width: 100px; max-height: 760px; overflow-y: auto; }
                .sidebar h3 { margin: 0 0 5px 0; font-size: 14px; color: #aaa; text-transform: uppercase; }
                .block-btn { display: flex; flex-direction: column; align-items: center; background: #444; border: 2px solid #666; border-radius: 4px; padding: 6px; cursor: pointer; color: white; font-size: 11px; transition: all 0.2s; }
                .block-btn img { width: 32px; height: 32px; margin-bottom: 4px; image-rendering: pixelated; }
                .block-btn:hover { background: #555; border-color: #888; }
                .block-btn.active { background: #4CAF50; border-color: #fff; box-shadow: 0 0 8px #4CAF50; }
            </style>
        </head>
        <body>
            <h1>WorldX Editor</h1>
            <div class="control-panel">
                <div id="coordinates">x: 0, y: 0</div>
                <div class="teleport-container">
                    <input type="text" id="teleportPosition" placeholder="x, y (e.g., 500, 300)" onkeydown="checkEnter(event)">
                    <button onclick="teleport()">Teleport</button>
                </div>
            </div>
            
            <div class="game-container">
                <canvas id="gameCanvas"></canvas>
                <div class="sidebar">
                    <h3>Bloky</h3>
                    <div id="palette"></div>
                </div>
            </div>

            <script>
                const canvasWidth = 1600;
                const canvasHeight = 800;

                const baseBlockSize = 40; 
                let currentBlockSize = 40; 
                
                let cameraR = 0; let cameraC = 0; let maxWorldSize = 1000;
                let currentMapView = [];
                let selectedBlockId = 0; 
                
                let isDrawing = false;   
                let isPanning = false;   
                let lastMouseX = 0;
                let lastMouseY = 0;

                let panXAccumulator = 0;
                let panYAccumulator = 0;

                const canvas = document.getElementById('gameCanvas'); const ctx = canvas.getContext('2d');
                canvas.width = canvasWidth; canvas.height = canvasHeight;

                canvas.addEventListener('contextmenu', e => e.preventDefault());

                const blocksConfig = {{ blocksBackend | tojson }};
                const totalBlocksCount = blocksConfig.length;
                
                const textures = {};
                let loadedImagesCount = 0;

                const paletteEl = document.getElementById('palette');
                blocksConfig.forEach((block, index) => {
                    const img = new Image();
                    img.src = `/static/${block.name}.png`;
                    img.onload = function() {
                        loadedImagesCount++;
                        if (loadedImagesCount === totalBlocksCount) {
                            loadMapChunk();
                        }
                    };
                    textures[block.id] = img;

                    const btn = document.createElement('div');
                    btn.className = `block-btn ${index === 0 ? 'active' : ''}`;
                    btn.dataset.id = block.id;
                    btn.innerHTML = `<img src="/static/${block.name}.png"><span>${block.name}</span>`;
                    btn.onclick = function() {
                        document.querySelectorAll('.block-btn').forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        selectedBlockId = block.id;
                    };
                    paletteEl.appendChild(btn);
                });

                function loadMapChunk() {
                    const dynamicCols = Math.ceil(canvasWidth / currentBlockSize);
                    const dynamicRows = Math.ceil(canvasHeight / currentBlockSize);

                    fetch(`/api/mapView?r=${Math.floor(cameraR)}&c=${Math.floor(cameraC)}&w=${dynamicCols}&h=${dynamicRows}`)
                        .then(res => res.json())
                        .then(data => {
                            currentMapView = data.map; maxWorldSize = data.maxSize;
                            renderMap();
                        });
                }

                function renderMap() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    if (!currentMapView.length) return;
                    
                    for (let r = 0; r < currentMapView.length; r++) {
                        for (let c = 0; c < currentMapView[r].length; c++) {
                            ctx.drawImage(
                                textures[currentMapView[r][c]], 
                                c * currentBlockSize, 
                                r * currentBlockSize, 
                                currentBlockSize, 
                                currentBlockSize
                            );
                        }
                    }
                }

                function checkEnter(e) { if (e.key === 'Enter') teleport(); }
                
                function teleport() {
                    const input = document.getElementById('teleportPosition').value; const parts = input.split(','); if (parts.length !== 2) return;
                    let targetX = parseInt(parts[0].trim()); let targetY = parseInt(parts[1].trim()); if (isNaN(targetX) || isNaN(targetY)) return;
                    
                    const dynamicCols = Math.ceil(canvasWidth / currentBlockSize);
                    const dynamicRows = Math.ceil(canvasHeight / currentBlockSize);
                    
                    let maxC = maxWorldSize - dynamicCols; let maxR = maxWorldSize - dynamicRows;
                    if (targetX < 0) targetX = 0; if (targetX > maxC) targetX = maxC;
                    if (targetY < 0) targetY = 0; if (targetY > maxR) targetY = maxR;
                    cameraC = targetX; cameraR = targetY; loadMapChunk();
                }

                // ZOOMOVANIE SMEROM KU KURZORU MYŠI
                canvas.addEventListener('wheel', function(e) {
                    e.preventDefault();
                    
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;

                    // 1. Zistíme presnú pozíciu vo svete pod myšou pred zoomom (vrátane desatinných miest)
                    const worldXBefore = cameraC + (mouseX / currentBlockSize);
                    const worldYBefore = cameraR + (mouseY / currentBlockSize);

                    let direction = e.deltaY > 0 ? -1 : 1;
                    let oldBlockSize = currentBlockSize;
                    let newBlockSize = currentBlockSize + (direction * 4);
                    
                    if (newBlockSize < 10) newBlockSize = 10;
                    if (newBlockSize > 80) newBlockSize = 80;
                    
                    if (oldBlockSize !== newBlockSize) {
                        currentBlockSize = newBlockSize;
                        
                        // 2. Prepočítame kameru tak, aby world pozícia zostala na rovnakom pixeli na obrazovke
                        let newCameraC = worldXBefore - (mouseX / currentBlockSize);
                        let newCameraR = worldYBefore - (mouseY / currentBlockSize);
                        
                        const dynamicCols = Math.ceil(canvasWidth / currentBlockSize);
                        const dynamicRows = Math.ceil(canvasHeight / currentBlockSize);
                        
                        // 3. Ošetrenie okrajov sveta
                        if (newCameraC < 0) newCameraC = 0;
                        if (newCameraC > maxWorldSize - dynamicCols) newCameraC = maxWorldSize - dynamicCols;
                        if (newCameraR < 0) newCameraR = 0;
                        if (newCameraR > maxWorldSize - dynamicRows) newCameraR = maxWorldSize - dynamicRows;
                        
                        cameraC = newCameraC;
                        cameraR = newCameraR;
                        
                        loadMapChunk();
                        updateCoordinates(e);
                    }
                });

                function updateCoordinates(e) {
                    const rect = canvas.getBoundingClientRect();
                    const clickC = Math.floor((e.clientX - rect.left) / currentBlockSize);
                    const clickR = Math.floor((e.clientY - rect.top) / currentBlockSize);
                    
                    let globalX = Math.floor(cameraC) + clickC;
                    let globalY = Math.floor(cameraR) + clickR;
                    
                    if (globalX >= 0 && globalX < maxWorldSize && globalY >= 0 && globalY < maxWorldSize) {
                        document.getElementById('coordinates').innerText = `x: ${globalX}, y: ${globalY}`;
                    }
                }

                function drawBlockAtMouse(e) {
                    const rect = canvas.getBoundingClientRect();
                    const clickC = Math.floor((e.clientX - rect.left) / currentBlockSize);
                    const clickR = Math.floor((e.clientY - rect.top) / currentBlockSize);
                    
                    if (clickR >= 0 && clickR < currentMapView.length && clickC >= 0 && clickC < currentMapView[0].length) {
                        if (currentMapView[clickR][clickC] !== selectedBlockId) {
                            let globalX = Math.floor(cameraC) + clickC; 
                            let globalY = Math.floor(cameraR) + clickR;
                            
                            currentMapView[clickR][clickC] = selectedBlockId;
                            ctx.drawImage(textures[selectedBlockId], clickC * currentBlockSize, clickR * currentBlockSize, currentBlockSize, currentBlockSize);
                            
                            fetch('/api/blockChange', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ x: globalX, y: globalY, newId: selectedBlockId })
                            });
                        }
                    }
                }

                canvas.addEventListener('mousedown', function(e) {
                    if (e.button === 0) { 
                        isDrawing = true;
                        drawBlockAtMouse(e);
                    } else if (e.button === 2) { 
                        isPanning = true;
                        lastMouseX = e.clientX;
                        lastMouseY = e.clientY;
                        panXAccumulator = 0;
                        panYAccumulator = 0;
                    }
                });

                canvas.addEventListener('mousemove', function(e) {
                    updateCoordinates(e);

                    if (isDrawing) {
                        drawBlockAtMouse(e);
                    } else if (isPanning) {
                        let deltaX = lastMouseX - e.clientX;
                        let deltaY = lastMouseY - e.clientY;
                        
                        lastMouseX = e.clientX;
                        lastMouseY = e.clientY;

                        panXAccumulator += deltaX / currentBlockSize;
                        panYAccumulator += deltaY / currentBlockSize;

                        let cameraChanged = false;
                        const dynamicCols = Math.ceil(canvasWidth / currentBlockSize);
                        const dynamicRows = Math.ceil(canvasHeight / currentBlockSize);

                        if (Math.abs(panXAccumulator) >= 0.5) {
                            let moveC = panXAccumulator > 0 ? Math.ceil(panXAccumulator) : Math.floor(panXAccumulator);
                            let newC = cameraC + moveC;
                            if (newC >= 0 && newC <= maxWorldSize - dynamicCols) {
                                cameraC = newC;
                                panXAccumulator -= moveC;
                                cameraChanged = true;
                            }
                        }

                        if (Math.abs(panYAccumulator) >= 0.5) {
                            let moveR = panYAccumulator > 0 ? Math.ceil(panYAccumulator) : Math.floor(panYAccumulator);
                            let newR = cameraR + moveR;
                            if (newR >= 0 && newR <= maxWorldSize - dynamicRows) {
                                cameraR = newR;
                                panYAccumulator -= moveR;
                                cameraChanged = true;
                            }
                        }

                        if (cameraChanged) {
                            loadMapChunk();
                        }
                    }
                });

                window.addEventListener('mouseup', function(e) {
                    if (e.button === 0) isDrawing = false;
                    if (e.button === 2) isPanning = false;
                });
            </script>
        </body>
        </html>
        """
        return render_template_string(htmlCode, blocksBackend=self.blockList)

    def startServer(self):
        self.app.run(host=self.host, port=self.port, debug=True, use_reloader=False)