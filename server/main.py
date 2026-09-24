import os
import game

webServerAddr = ("0.0.0.0", 5000)
TCPCommAddr = ("0.0.0.0", 5001)

game = game.Game(TCPCommAddr, webServerAddr)
