import socket
import threading
import time
import uuid
import os
from blessed import Terminal
import json

def getAccountId():
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accountId.txt")
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read().strip()
    else:
        id = str(uuid.uuid4())
        with open(filename, "w") as f:
            f.write(id)
        return id

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
        self.sendMessage(f"login:{getAccountId()}", True)
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

client = Client(("192.168.0.154", 5001))

def forward():
    client.sendMessage("forward")

def turn_left():
    client.sendMessage("left")

def turn_right():
    client.sendMessage("right")

def turn_towards(dir):
    client.sendMessage(f"turnTo:{dir}")

def get_position():
    return client.sendMessage('getPos')

def is_pressed(klaves):
    char = klaves.lower()
    if char in client.pressedKeys:
        client.pressedKeys.remove(char)
        return True
    return False

def interact(action):
    return client.sendMessage(f'interact:{action}')

def attack():
    client.sendMessage('attack')

def equip(item, slot):
    client.sendMessage(f'equip:{item}|{slot}')

def unequip(slot):
    client.sendMessage(f'unequip:{slot}')

def setSkin(asciiSkin):
    client.sendMessage(f'setSkin:{asciiSkin}')
