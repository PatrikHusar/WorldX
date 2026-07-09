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
            <title>WorldX Game</title>
            <style>
                body { font-family: Arial, sans-serif; background: #222; color: white; text-align: center; margin: 0; padding: 5px 10px; user-select: none; overflow-y: hidden; }
                h1 { margin-top: 5px; margin-bottom: 5px; font-size: 24px; }
                .control-panel { display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 5px; }
                #coordinates { font-weight: bold; color: #4CAF50; font-size: 16px; }
                .teleport-container input { padding: 6px; font-size: 13px; border: 1px solid #666; border-radius: 4px; background: #333; color: white; text-align: center; width: 120px; }
                .teleport-container button { padding: 6px 12px; font-size: 13px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px; font-weight: bold; }
                .teleport-container button:hover { background: #45a049; }
                #gameCanvas { border: 4px solid #555; background: #000; margin: 0 auto; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); cursor: crosshair; }
            </style>
        </head>
        <body>
            <h1>WorldX</h1>
            <div class="control-panel">
                <div id="coordinates">x: 0, y: 0</div>
                <div class="teleport-container">
                    <input type="text" id="teleportPosition" placeholder="x, y (e.g., 500, 300)" onkeydown="checkEnter(event)">
                    <button onclick="teleport()">Teleport</button>
                </div>
            </div>
            <canvas id="gameCanvas"></canvas>

            <script>
                const visibleColumns = 40; const visibleRows = 20; const blockSize = 40; 
                let cameraR = 0; let cameraC = 0; let maxWorldSize = 1000;
                const canvas = document.getElementById('gameCanvas'); const ctx = canvas.getContext('2d');
                canvas.width = visibleColumns * blockSize; canvas.height = visibleRows * blockSize;

                // Tu Flask automaticky vloží zoznam blokov z Pythonu do JavaScriptového poľa
                const blocksConfig = {{ blocksBackend | tojson }};
                const totalBlocksCount = blocksConfig.length; // Dynamický počet blokov
                
                const textures = {};
                let loadedImagesCount = 0;

                // Automatické dynamické načítanie všetkých obrázkov podľa konfigurácie
                blocksConfig.forEach(block => {
                    const img = new Image();
                    img.src = `/static/${block.name}.png`;
                    img.onload = function() {
                        loadedImagesCount++;
                        // Keď sa načítajú úplne všetky obrázky zo zoznamu, načítame prvý kus mapy
                        if (loadedImagesCount === totalBlocksCount) {
                            loadMapChunk();
                        }
                    };
                    textures[block.id] = img;
                });

                function loadMapChunk() {
                    fetch(`/api/mapView?r=${cameraR}&c=${cameraC}&w=${visibleColumns}&h=${visibleRows}`)
                        .then(res => res.json())
                        .then(data => {
                            currentMapView = data.map; maxWorldSize = data.maxSize;
                            document.getElementById('coordinates').innerText = `x: ${cameraC}, y: ${cameraR}`;
                            renderMap();
                        });
                }

                function renderMap() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    for (let r = 0; r < currentMapView.length; r++) {
                        for (let c = 0; c < currentMapView[r].length; c++) {
                            ctx.drawImage(textures[currentMapView[r][c]], c * blockSize, r * blockSize, blockSize, blockSize);
                        }
                    }
                }

                function checkEnter(e) { if (e.key === 'Enter') teleport(); }
                
                function teleport() {
                    const input = document.getElementById('teleportPosition').value; const parts = input.split(','); if (parts.length !== 2) return;
                    let targetX = parseInt(parts[0].trim()); let targetY = parseInt(parts[1].trim()); if (isNaN(targetX) || isNaN(targetY)) return;
                    let maxC = maxWorldSize - visibleColumns; let maxR = maxWorldSize - visibleRows;
                    if (targetX < 0) targetX = 0; if (targetX > maxC) targetX = maxC;
                    if (targetY < 0) targetY = 0; if (targetY > maxR) targetY = maxR;
                    cameraC = targetX; cameraR = targetY; loadMapChunk();
                }

                canvas.addEventListener('wheel', function(e) {
                    e.preventDefault(); let direction = e.deltaY > 0 ? 1 : -1;
                    if (e.shiftKey) {
                        let newC = cameraC + (direction * 2); if (newC >= 0 && newC <= maxWorldSize - visibleColumns) cameraC = newC;
                    } else {
                        let newR = cameraR + (direction * 2); if (newR >= 0 && newR <= maxWorldSize - visibleRows) cameraR = newR;
                    }
                    loadMapChunk();
                });

                canvas.addEventListener('click', function(e) {
                    const rect = canvas.getBoundingClientRect();
                    const clickC = Math.floor((e.clientX - rect.left) / blockSize);
                    const clickR = Math.floor((e.clientY - rect.top) / blockSize);
                    if (clickR >= 0 && clickR < currentMapView.length && clickC >= 0 && clickC < currentMapView[0].length) {
                        // MODULO JE TU DYNAMICKÉ PODĽA POČTU BLOKOV V ZOZNAME
                        let newId = (currentMapView[clickR][clickC] + 1) % totalBlocksCount; 
                        let globalX = cameraC + clickC; let globalY = cameraR + clickR;
                        
                        currentMapView[clickR][clickC] = newId;
                        ctx.drawImage(textures[newId], clickC * blockSize, clickR * blockSize, blockSize, blockSize);
                        fetch('/api/blockChange', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ x: globalX, y: globalY, newId: newId })
                        });
                    }
                });
            </script>
        </body>
        </html>
        """
        return render_template_string(htmlCode, blocksBackend=self.blockList)

    def startServer(self):
        self.app.run(host=self.host, port=self.port, debug=True)