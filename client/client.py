import socket

class Client:
    def __init__(self, adress) -> None:
        self.__adress = adress
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect(self.__adress)

    def sendMessage(self, message):
        self.__client.sendall(message.encode("utf-8"))
        response = self.__client.recv(1024).decode("utf-8")
        return response
    
    def closeConnection(self):
        self.__client.close()

client = Client(("127.0.0.1", 65432))

def forward():
    client.sendMessage('forward')
def turn_left():
    client.sendMessage('left')
def turn_right():
    client.sendMessage('right')
def turn_towards(dir):
    client.sendMessage(f'turnTo:{dir}')
def login(password):
    client.sendMessage(f'login:{password}')