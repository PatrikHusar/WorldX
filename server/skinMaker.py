import os
import colorsys
from PIL import Image
import random

class SkinMaker:
    def __init__(self, outputFolder, asciiSize=(32, 122), imgSize=(42, 42)):
        self.asciiSize = asciiSize
        self.imgSize = imgSize
        self.outputFolder = outputFolder

    def getCharColor(self, char):
        minAscii, maxAscii = self.asciiSize
        r, g, b = colorsys.hsv_to_rgb((max(minAscii, min(maxAscii, ord(char) if isinstance(char, str) and len(char) == 1 else minAscii)) - minAscii) / float(maxAscii - minAscii + 1), 0.95, 0.95)
        return (int(r * 255), int(g * 255), int(b * 255), 255)
    
    def getColorChar(self, rgba):
        minAscii, maxAscii = self.asciiSize
        return chr(int(max(minAscii, min(maxAscii, round(colorsys.rgb_to_hsv(rgba[0] / 255.0, rgba[1] / 255.0, rgba[2] / 255.0)[0] * maxAscii - minAscii + 1) + minAscii))))

    def createSkin(self, name, asciiSkin):
        if not isinstance(asciiSkin, str) or not asciiSkin:
            img = Image.new("RGBA", (1, 1), (0, 0, 0, 255))
            pixels = img.load()
            pixels[0, 0] = self.getCharColor(chr(random.randint(self.asciiSize[0], self.asciiSize[1])))
        else:
            lines = asciiSkin.splitlines()
            img = Image.new("RGBA", (max(len(row) for row in lines), len(lines)), (0, 0, 0, 255))
            pixels = img.load()
            for y, row in enumerate(lines):
                for x, char in enumerate(row):
                    pixels[x, y] = self.getCharColor(char)

        # resizes and saves image
        folderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.outputFolder)
        os.makedirs(folderPath, exist_ok=True)
        img.resize(self.imgSize, Image.NEAREST).save(os.path.join(folderPath, f"{name}.png"), "PNG")
    
    def changeImageTransparency(self, name, transparency):
        folderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.outputFolder)
        fileName = f"{name}.png"
        imagePath = os.path.join(folderPath, fileName)
        factor = max(0.0, min(float(transparency), 1.0))
        with Image.open(imagePath) as img:
            img = img.convert("RGBA")
            alpha = img.getchannel('A').point(lambda p: int(p * factor))
            img.putalpha(alpha)
            outputPath = os.path.join(folderPath, fileName)
            img.save(outputPath, "PNG")
