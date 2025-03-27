
import zlib
import struct

# --- doc used : 
# https://stackoverflow.com/questions/8554282/creating-a-png-file-in-python

# obj GreyImgManager, use to create an image (write/read pixels, and save) only grey pixel value.
class GreyImgManager():
    def __init__(self):
        self.pixels = [] # the 2D list of every pixels.
        self.defaultPixel = None # the pixel set by default when a pixel has no values.

    # return the height size of img.
    def getHeight(self):
        return len(self.pixels)

    # return the width size of img (return the length of the bigest line).
    def getWidth(self):
        return max(list(map(lambda l: len(l), self.pixels)))

    # apply a pixel to a position in img.
    def setPixel(self, x:int, y:int, pixel:int):

        while(len(self.pixels) <= y): # add line until img has enough line to have index.
            self.pixels.append([])

        while(len(self.pixels[y]) <= x): # add pixel until line has enough to have index.
            self.pixels[y].append(self.defaultPixel)

        self.pixels[y][x] = pixel # write the pixel.

    # return the pixel at the pos index ask.
    def getPixel(self, x:int, y:int):
        if(y < len(self.pixels) and x < len(self.pixels[y])):
            return self.pixels[y][x]
        else:
            return self.defaultPixel

    # make a byte of the png content.
    def makePNGbyte(self):

        # doc used : https://stackoverflow.com/questions/8554282/creating-a-png-file-in-python (Copyright (C) 2014 Guido Draheim) (Public Domain)
        def I1(value):
            return struct.pack("!B", value & (2**8-1))
        def I4(value):
            return struct.pack("!I", value & (2**32-1))

        # generate these chunks depending on image type
        makeIHDR = True
        makeIDAT = True
        makeIEND = True
        png = b"\x89" + "PNG\r\n\x1A\n".encode('ascii')
        if makeIHDR:
            colortype = 0 # true gray image (no palette)
            bitdepth = 8 # with one byte per pixel (0..255)
            compression = 0 # zlib (no choice here)
            filtertype = 0 # adaptive (each scanline seperately)
            interlaced = 0 # no
            IHDR = I4(self.getWidth()) + I4(self.getHeight()) + I1(bitdepth)
            IHDR += I1(colortype) + I1(compression)
            IHDR += I1(filtertype) + I1(interlaced)
            block = "IHDR".encode('ascii') + IHDR
            png += I4(len(IHDR)) + block + I4(zlib.crc32(block))
        if makeIDAT:
            raw = b""
            for y in range(self.getHeight()):
                raw += b"\0" # no filter for this scanline
                for x in range(self.getWidth()):
                    c = b"\0" # default black pixel
                    pixel = self.getPixel(x, y)
                    if(pixel != None):
                        c = I1(pixel)
                    raw += c
            compressor = zlib.compressobj()
            compressed = compressor.compress(raw)
            compressed += compressor.flush() #!!
            block = "IDAT".encode('ascii') + compressed
            png += I4(len(compressed)) + block + I4(zlib.crc32(block))
        if makeIEND:
            block = "IEND".encode('ascii')
            png += I4(0) + block + I4(zlib.crc32(block))
        return png

    # save img in PNG file.
    def saveAsPNG(self, path:str):
        with open(path, "wb") as file:
            file.write(self.makePNGbyte())
            
