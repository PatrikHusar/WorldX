import socket
import threading

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
        loginData = self.getMessage(client, adress)
        response = self.processClientData(loginData, adress[0])
        self.sendMessage(client, response)
        while True:
            data = self.getMessage(client, adress)
            if not data:
                break
            response = self.processClientData(data, adress[0])
            self.sendMessage(client, response)

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

    def getMessage(self, client, adress):
        try:
            data = client.recv(1024).decode("utf-8")
            if not data:
                self.closeConnection(client, adress)
                return None
            return data
        except:
            self.closeConnection(client, adress)
            return None
    
    def sendMessage(self, client, message):
        try:
            client.sendall(message.encode("utf-8"))
        except:
            pass
        
    def closeConnection(self, client, adress):
        if client in self.clients:
            print(f"Client disconnected: {adress[0]}:{adress[1]}")
            try:
                client.close()
            except:
                pass
            if client in self.clients:
                self.clients.remove(client)
            if adress in self.adresses:
                self.adresses.remove(adress)
