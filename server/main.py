import os
import game

game = game.Game(int(os.environ.get("PORT", 5000)))
