import socket

class Client:
    def __init__(self, adress) -> None:
        self.__adress = adress
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect(self.__adress)
        self.__closeConnection()
    
    def sendMessage(self, message):
        self.__client.sendall(message.encode("utf-8"))
        response = self.__client.recv(1024).decode("utf-8")
        return response
    
    def __closeConnection(self):
        self.__client.close()

client = Client(("127.0.0.1", 65432))
