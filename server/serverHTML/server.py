import random
from flask import Flask, jsonify, request, render_template_string


class serverHTML:

    def __init__(self, host, port):
        self.app = Flask(__name__)
        self.host = host
        self.port = port

        self.velkost_sveta = 1000
        self.moj_svet = []
        self.vygeneruj_novy_svet()

        self.app.add_url_rule("/", "index", self.stranka_index)
        self.app.add_url_rule("/api/vyrez", "vyrez", self.daj_vyrez_json)

    def vygeneruj_novy_svet(self):
        print("Generujem obrovský svet 1000x1000 v pamäti...")
        self.moj_svet = [
            [random.choice([0, 0, 0, 1, 2]) for _ in range(self.velkost_sveta)]
            for _ in range(self.velkost_sveta)
        ]
        print("Svet vygenerovaný!")

    def daj_vyrez_json(self):
        start_r = int(request.args.get("r", 0))
        start_s = int(request.args.get("s", 0))
        sirka = int(request.args.get("w", 40))
        vyska = int(request.args.get("h", 20))

        vyrez = []
        for r in range(start_r, min(start_r + vyska, self.velkost_sveta)):
            riadok = []
            for s in range(start_s, min(start_s + sirka, self.velkost_sveta)):
                riadok.append(self.moj_svet[r][s])
            vyrez.append(riadok)

        return jsonify(
            {
                "mapa": vyrez,
                "start_r": start_r,
                "start_s": start_s,
                "max_velkost": self.velkost_sveta,
            }
        )

    def stranka_index(self):
        html_kod = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>1000x1000 Svet</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: #222; 
                    color: white; 
                    text-align: center; 
                    margin: 0; 
                    padding: 5px 10px; 
                    user-select: none;
                    overflow-y: hidden; 
                }
                
                h1 { 
                    margin-top: 5px; 
                    margin-bottom: 5px; 
                    font-size: 24px; 
                }
                
                .ovladaci-panel {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 20px; 
                    margin-bottom: 5px; 
                }
                
                #suradnice { 
                    font-weight: bold; 
                    color: #4CAF50; 
                    font-size: 16px; 
                }
                
                .teleport-kontajner input {
                    padding: 6px;
                    font-size: 13px;
                    border: 1px solid #666;
                    border-radius: 4px;
                    background: #333;
                    color: white;
                    text-align: center;
                    width: 110px;
                }
                .teleport-kontajner button {
                    padding: 6px 12px;
                    font-size: 13px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-left: 5px;
                    font-weight: bold;
                }
                .teleport-kontajner button:hover { background: #45a049; }

                #hernePlatno {
                    border: 4px solid #555;
                    background: #000;
                    margin: 0 auto;
                    box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
                    cursor: crosshair;
                }
            </style>
        </head>
        <body>
            <h1>Svet 1000x1000</h1>
            
            <div class="ovladaci-panel">
                <div id="suradnice">x: 0, y: 0</div>
                
                <div class="teleport-kontajner">
                    <input type="text" id="teleportPozicia" placeholder="x, y (napr. 500, 300)" onkeydown="skontrolujEnter(event)">
                    <button onclick="teleportuj()">Teleport</button>
                </div>
            </div>
            
            <canvas id="hernePlatno"></canvas>

            <script>
                const viditelneStlpce = 40;
                const viditelneRiadky = 20;
                const velkostBloku = 40; 

                let kameraR = 0; 
                let kameraS = 0; 
                let maxVelkostSveta = 1000;

                const canvas = document.getElementById('hernePlatno');
                const ctx = canvas.getContext('2d');
                
                canvas.width = viditelneStlpce * velkostBloku;
                canvas.height = viditelneRiadky * velkostBloku;

                const imgGrass = new Image(); imgGrass.src = '/static/grass.png';
                const imgWater = new Image(); imgWater.src = '/static/water.png';
                const imgTree = new Image();  imgTree.src = '/static/tree.png';

                const obrazky = { 0: imgGrass, 1: imgWater, 2: imgTree };
                let aktualnyVyrez = [];

                let nacitaneObrazky = 0;
                function skontrolujObrazky() {
                    nacitaneObrazky++;
                    if (nacitaneObrazky === 3) nacitajKusokMapy();
                }
                imgGrass.onload = skontrolujObrazky;
                imgWater.onload = skontrolujObrazky;
                imgTree.onload = skontrolujObrazky;

                function nacitajKusokMapy() {
                    fetch(`/api/vyrez?r=${kameraR}&s=${kameraS}&w=${viditelneStlpce}&h=${viditelneRiadky}`)
                        .then(response => response.json())
                        .then(data => {
                            aktualnyVyrez = data.mapa;
                            maxVelkostSveta = data.max_velkost;
                            document.getElementById('suradnice').innerText = `x: ${kameraS}, y: ${kameraR}`;
                            vykresliZobrazenuMapu();
                        });
                }

                function vykresliZobrazenuMapu() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    for (let r = 0; r < aktualnyVyrez.length; r++) {
                        for (let s = 0; s < aktualnyVyrez[r].length; s++) {
                            let typ = aktualnyVyrez[r][s];
                            ctx.drawImage(obrazky[typ], s * velkostBloku, r * velkostBloku, velkostBloku, velkostBloku);
                        }
                    }
                }

                // PRIDANÉ: Funkcia zachytávajúca kláves Enter
                function skontrolujEnter(event) {
                    if (event.key === 'Enter') {
                        teleportuj();
                    }
                }

                function teleportuj() {
                    const input = document.getElementById('teleportPozicia').value;
                    const casti = input.split(',');
                    
                    if (casti.length !== 2) {
                        alert("Zadaj pozíciu v správnom formáte: x, y");
                        return;
                    }

                    let cieloveX = parseInt(casti[0].trim());
                    let cieloveY = parseInt(casti[1].trim());

                    if (isNaN(cieloveX) || isNaN(cieloveY)) {
                        alert("Súradnice musia byť čísla!");
                        return;
                    }

                    let maxS = maxVelkostSveta - viditelneStlpce;
                    let maxR = maxVelkostSveta - viditelneRiadky;

                    if (cieloveX < 0) cieloveX = 0;
                    if (cieloveX > maxS) cieloveX = maxS;
                    if (cieloveY < 0) cieloveY = 0;
                    if (cieloveY > maxR) cieloveY = maxR;

                    kameraS = cieloveX;
                    kameraR = cieloveY;

                    nacitajKusokMapy();
                }

                canvas.addEventListener('wheel', function(event) {
                    event.preventDefault();
                    let smer = event.deltaY > 0 ? 1 : -1;
                    const rychlostPosunu = 2;

                    if (event.shiftKey) {
                        let novaS = kameraS + (smer * rychlostPosunu);
                        if (novaS >= 0 && novaS <= maxVelkostSveta - viditelneStlpce) {
                            kameraS = novaS;
                        }
                    } else {
                        let novaR = kameraR + (smer * rychlostPosunu);
                        if (novaR >= 0 && novaR <= maxVelkostSveta - viditelneRiadky) {
                            kameraR = novaR;
                        }
                    }
                    nacitajKusokMapy();
                });

                canvas.addEventListener('click', function(event) {
                    const rect = canvas.getBoundingClientRect();
                    const klikX = event.clientX - rect.left;
                    const klikY = event.clientY - rect.top;

                    const zobrazenyStlpec = Math.floor(klikX / velkostBloku);
                    const zobrazenyRiadok = Math.floor(klikY / velkostBloku);

                    if (zobrazenyRiadok >= 0 && zobrazenyRiadok < aktualnyVyrez.length && 
                        zobrazenyStlpec >= 0 && zobrazenyStlpec < aktualnyVyrez[0].length) {
                        
                        let aktualnyTyp = aktualnyVyrez[zobrazenyRiadok][zobrazenyStlpec];
                        let novyTyp = (aktualnyTyp + 1) % 3;

                        aktualnyVyrez[zobrazenyRiadok][zobrazenyStlpec] = novyTyp;
                        ctx.drawImage(obrazky[novyTyp], zobrazenyStlpec * velkostBloku, zobrazenyRiadok * velkostBloku, velkostBloku, velkostBloku);
                    }
                });
            </script>
        </body>
        </html>
        """
        return render_template_string(html_kod)

    def spust_server(self):
        self.app.run(host=self.host, port=self.port, debug=True)


if __name__ == "__main__":
    server = serverHTML(host="0.0.0.0", port=5000)
    server.spust_server()