import socket

class Client:
    def __init__(self, adress) -> None:
        self.__adress = adress
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect(self.__adress)

    def sendMessage(self, message):
        try:
            self.__client.sendall(message.encode("utf-8"))
            response = self.__client.recv(1024).decode("utf-8")
            print(f'responded: {response}')
            return response
        except Exception as e:
            print(f"comm error: {e}")
            return None
    
    def closeConnection(self):
        self.__client.close()

client = Client(("127.0.0.1", 65432))

def forward():
    return client.sendMessage('forward')

def turn_left():
    return client.sendMessage('left')

def turn_right():
    return client.sendMessage('right')

def turn_towards(dir):
    return client.sendMessage(f'turnTo:{dir}')

def login(password):
    return client.sendMessage(f'login:{password}')