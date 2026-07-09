import random
from flask import Flask, jsonify, render_template_string

class serverHTML:

    def __init__(self, host, port):
        self.app = Flask(__name__)
        self.host = host
        self.port = port

        self.velkost_sveta = 10
        self.moj_svet = []
        self.vygeneruj_novy_svet()

        self.app.add_url_rule("/", "index", self.stranka_index)
        self.app.add_url_rule("/api/mapa", "mapa", self.daj_mapu_json)

    def vygeneruj_novy_svet(self):
        self.moj_svet = [
            [
                random.choice([0, 0, 0, 1])
                for _ in range(self.velkost_sveta)
            ]
            for _ in range(self.velkost_sveta)
        ]

    def daj_mapu_json(self):
        return jsonify(self.moj_svet)

    def stranka_index(self):
        html_kod = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Moja Hra v Classe</title>
            <style>
                body { font-family: Arial, sans-serif; background: #222; color: white; text-align: center; }
                #mapa-kontajner { 
                    display: grid; 
                    grid-template-columns: repeat(10, 40px);
                    gap: 2px; 
                    justify-content: center; 
                    margin-top: 20px;
                }
                .dlazdica { width: 40px; height: 40px; border-radius: 4px; }
                .trava { background-color: #4CAF50; }
                .voda { background-color: #2196F3; }
            </style>
        </head>
        <body>
            <h1>Mapa sveta z Python Classy</h1>
            <div id="mapa-kontajner"></div>

            <script>
                fetch('/api/mapa')
                    .then(response => response.json())
                    .then(mapa => {
                        const kontajner = document.getElementById('mapa-kontajner');
                        for (let r = 0; r < mapa.length; r++) {
                            for (let s = 0; s < mapa[r].length; s++) {
                                const div = document.createElement('div');
                                div.classList.add('dlazdica');
                                if (mapa[r][s] === 0) div.classList.add('trava');
                                else div.classList.add('voda');
                                kontajner.appendChild(div);
                            }
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