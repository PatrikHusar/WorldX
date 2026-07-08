import socket

class Client:
    def __init__(self, adress) -> None:
        self.adress = adress
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.adress)
        # self.close_connection()
    
    def sendMessage(self, message):
        self.client.sendall(message.encode("utf-8"))
        response = self.client.recv(1024).decode("utf-8")
        return response
    
    def closeConnection(self):
        self.client.close()

client = Client(("127.0.0.1", 65432))
