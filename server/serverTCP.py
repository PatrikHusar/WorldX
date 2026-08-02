import socket
import threading
import json

class Server:
    def __init__(self, adress, processClientData) -> None:
        self.adress = adress
        self.processClientData = processClientData
        self.clients = []
        self.adresses = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.adress)
        self.server.listen()
        print(f"Server running on: {self.adress[0]}:{self.adress[1]}")
        threading.Thread(target=self.acceptConns, daemon=True).start()

    def clientLoop(self, client, adress):
        loginData = self.getMessage(client)
        response = self.processClientData(loginData, adress[0])
        self.sendMessage(client, response)
        while True:
            data = self.getMessage(client)
            if not data:
                break
            response = self.processClientData(data, adress[0])
            self.sendMessage(client, response)
        self.closeConnection(client, adress)

    def acceptConns(self):
        while True:
            try:
                client, adress = self.server.accept()
                self.clients.append(client)
                self.adresses.append(adress)
                print(f"Client connected: {adress[0]}:{adress[1]}")
                threading.Thread(target=self.clientLoop, args=(client, adress), daemon=True).start()
            except Exception as e:
                break

    def getMessage(self, client):
        try:
            data = client.recv(1024).decode("utf-8")
            if not data or data == 'disconnect':
                return None
            return data
        except:
            return None
    
    def sendMessage(self, client, message):
        try:
            client.sendall(json.dumps(message).encode("utf-8"))
        except:
            pass
        
    def closeConnection(self, client, adress):
        print(f"Client disconnected: {adress[0]}:{adress[1]}")
        client.close()
        self.clients.remove(client)
        self.adresses.remove(adress)
        self.processClientData('disconnect', adress[0])
