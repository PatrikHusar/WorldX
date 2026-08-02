import socket
import threading
import time
from blessed import Terminal
import json

class Client:
    def __init__(self, adress) -> None:
        self.__adress = adress
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connecting = True
        self.pressedKeys = set()
        self.physicalyPressed = set()
        self.lastKeyTime = 0
        self.__running = True
        self.term = Terminal()
        while connecting:
            try:
                self.__client.connect(self.__adress)
                connecting = False
            except:
                time.sleep(1)
                print("waiting for server to start.")
        print("connected to server")
        self.input_thread = threading.Thread(target=self.__loop_input, daemon=True).start()

    def __loop_input(self):
        with self.term.cbreak():
            while self.__running:
                char = self.term.inkey(timeout=0.02)

                if char:
                    charLower = char.lower()
                    self.lastKeyTime = time.time()

                    if charLower not in self.physicalyPressed:
                        self.pressedKeys.add(charLower)
                        self.physicalyPressed.add(charLower)
                else:
                    if time.time() - self.lastKeyTime > 0.08:
                        self.physicalyPressed.clear()

    def sendMessage(self, message, printResponse=False):
        try:
            self.__client.sendall(message.encode("utf-8"))
            response = json.loads(self.__client.recv(1024).decode("utf-8"))
            if response and printResponse:
                print(response)
            return response
        except Exception as e:
            print(f"comm error: {e}")
            print('closing communication..')
            self.closeConnection()
            return None

    def closeConnection(self):
        self.__running = False
        self.__client.close()

client = Client(("0.0.0.0", 65432))

def forward():
    client.sendMessage("forward")

def turn_left():
    client.sendMessage("left")

def turn_right():
    client.sendMessage("right")

def turn_towards(dir):
    client.sendMessage(f"turnTo:{dir}")

def login(password):
    return client.sendMessage(f"login:{password}", True)

def get_position():
    return client.sendMessage('getPos')

def is_pressed(klaves):
    char = klaves.lower()
    if char in client.pressedKeys:
        client.pressedKeys.remove(char)
        return True
    return False
