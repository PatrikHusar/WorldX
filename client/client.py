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
        self.last_key_time = 0
        self.__running = True
        self.term = Terminal()
        while connecting:
            try:
                self.__client.connect(self.__adress)
                connecting = False
            except:
                time.sleep(1)
                print("waiting for server to start.")
        print("connected to server, have fun!")
        self.input_thread = threading.Thread(target=self.__loop_input, daemon=True).start()

    def __loop_input(self):
        with self.term.cbreak():
            while self.__running:
                char = self.term.inkey(timeout=0.02)

                if char:
                    char_lower = char.lower()
                    self.last_key_time = time.time()

                    if char_lower not in self.physicalyPressed:
                        self.pressedKeys.add(char_lower)
                        self.physicalyPressed.add(char_lower)
                else:
                    if time.time() - self.last_key_time > 0.08:
                        self.physicalyPressed.clear()

    def sendMessage(self, message):
        try:
            self.__client.sendall(message.encode("utf-8"))
            response = json.loads(self.__client.recv(1024).decode("utf-8"))
            print(f"responded: {response}")
            return response
        except Exception as e:
            print(f"comm error: {e}")
            return None

    def closeConnection(self):
        self.__running = False
        self.__client.close()

client = Client(("192.168.0.154", 5001))

def forward():
    client.sendMessage("forward")

def turn_left():
    client.sendMessage("left")

def turn_right():
    client.sendMessage("right")

def turn_towards(dir):
    client.sendMessage(f"turnTo:{dir}")

def login(password):
    return client.sendMessage(f"login:{password}")

def get_position():
    return client.sendMessage('getPos')

def is_pressed(klaves):
    char = klaves.lower()
    if char in client.pressedKeys:
        client.pressedKeys.remove(char)
        return True
    return False
