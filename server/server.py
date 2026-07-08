import socket
import threading

class Server:
    def __init__(self, adress) -> None:
        self.adress = adress
        self.clients = []
        self.adresses = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.adress)
        self.server.listen()
        print(f"Server running on: {self.adress[0]}:{self.adress[1]}")
        self.acceptConns()
    
    def clientLoop(self, client, adress):
        while True:
            data = self.getMessage(client, adress)
            if not data:
                break
            

    def acceptConns(self):
        while True:
            client, adress = self.server.accept()
            self.clients.append(client)
            self.adresses.append(adress)
            print(f"client connected: {adress[0]}:{adress[1]}")
            threading.Thread(target=self.clientLoop, args=(client, adress)).start()


    def getMessage(self, client, adress):
        try:
            data = client.recv(1024).decode("utf-8")
            if not data:
                    self.closeConnection(client, adress)
        except:
            self.closeConnection(client, adress)
        return data
    
    def sendMessage(self, client, message):
        client.sendall(message.encode("utf-8"))
        
    def closeConnection(self, client, adress):
        try:
            client.close()
            self.clients.remove(client)
            self.adresses.remove(adress)
        except:
            pass


server = Server((("127.0.0.1", 65432)))
