from Class.GreyImgManager import GreyImgManager
import random

# doc use : https://youtu.be/s4Qo0g-bgMY?si=ehuFZPE437iquP1b (The Unqualified Tutor)
# doc use : https://youtu.be/w5ebcowAJD8?si=pwwYsXoTy7m7CjI0 (Veritasium)
# doc use : https://en.wikipedia.org/wiki/QR_code (Wiki)

# obj QRCodeManager make an img QR code from a string data.
class QRCodeManager(GreyImgManager):
    def __init__(self):
        super().__init__()
        self.data = ""
        self.mask = 2 # mask patern default 2 (between 0 to 7).
        self.binaryEncoding = 4 # binary encoding default 4 (1:numeric, 2:alphanumeric, 4:binary, 8:japanese kanji).
        self.size = None

    # set data.
    def setData(self, data:str):
        self.data = data

    # cast data to bin data (list of int) 0 to 255.
    def dataToBin(self):
        return list(map(lambda c: ord(c), self.data))
        
    # return the quantity of pixel need to print the binary data. TODO ? include length for verification.
    def evalPixelLengthForBinData(self, dataBin:list):
        return len(dataBin) * 8

    # try many size of QR code, until find the good size to fit data.
    def evalSizeImgForFitData(self, dataBinLenght:int):
        size = 9*2 +1 +4 # min size for fit 3 border square.
        isDataFit = False
        while(not isDataFit):
            if(self.evalPixelLengthCanFitOnASize(size) >= dataBinLenght):
                break
            size+=4
        return size

    # return the quantity of pixel can be write in a QR code size send.
    def evalPixelLengthCanFitOnASize(self, size:int):
        imgPixels = pow(size, 2)

        pixelsCantUse = 0 # eval pixels can't be use for data.
        pixelsCantUse += size * 4 -4 # border white.
        pixelsCantUse += 8 * 8 *3 # 3 border square.
        pixelsCantUse += (size - 9*2) *2 # 2 alternate band.
        if(size > 23): # no little square if size is to smal.
            littleSquareCount = 0
            sizeRef = size -5
            while(True):
                sizeRef -= 15 +5 
                littleSquareCount += 1
                if(sizeRef < 11):
                    break
            if(littleSquareCount == 1): # add only one little square.
                pixelsCantUse += 5*5
            else:
                pixelsCantUse += (pow(littleSquareCount, 2) -3) * (5*5) - ((littleSquareCount-2) *2 *5)
        pixelsCantUse += 8*2 + 15 # grey used border of 3 square border.
        pixelsCantUse += 12 # 12 first pixels for format.

        return imgPixels - pixelsCantUse

    # overide setPixel by sending bool (true = black).
    def setPixel(self, x:int, y:int, pixelValue:bool):
        super().setPixel(x, y, 0 if pixelValue else 255)

    # draw border white.
    def drawBorderWhite(self):
        for i in range(self.size):
            self.setPixel(i, 0, False)
            self.setPixel(i, self.size-1, False)
            self.setPixel(0, i, False)
            self.setPixel(self.size-1, i, False)

    # draw border square.
    def drawBorderSquare(self):
        for pos in [[0,0], [self.size-9,0], [0,self.size-9]]:
            for x in range(9):
                for y in range(9):
                    xb = 4-abs(x-4)
                    yb = 4-abs(y-4)
                    isBlack = min(xb,yb)%2 == 1
                    self.setPixel(x+pos[0], y+pos[1], isBlack)
            self.setPixel(4+pos[0], 4+pos[1], True)

    # draw alternet band.
    def drawAlternetBand(self):
        for i in range(self.size - 9*2):
            isBlack = i % 2 == 0
            self.setPixel(9+i, 7, isBlack)
            self.setPixel(7, 9+i, isBlack)

    # draw every little square.
    def drawLittleSquare(self):
        def printLittleSquare(QR, pos):
            for x in range(5):
                for y in range(5):
                    xb = 2-abs(x-2)
                    yb = 2-abs(y-2)
                    isBlack = min(xb,yb)%2 == 0
                    QR.setPixel(x+pos[0], y+pos[1], isBlack)

        pos = [self.size-10, self.size-10] # pos ref (first little square bottom right).
        x = 0
        y = 0
        while(True):
            yb = pos[1] - y*20
            if(yb < 0): # finish last line.
                break
            while(True):
                xb = pos[0] - x*20
                if(xb < 0): # finis last cel of line.
                    x=0
                    break

                isSquareUpLeft = (yb-20 < 0 and xb-20 < 0) # skip little square in big one.
                isSquareDonwLeft = (y==0 and xb-20 < 0)
                isSuareUpRight = (yb-20 < 0 and x==0)
                if((isSquareUpLeft or isSquareDonwLeft or isSuareUpRight) and not(isSquareDonwLeft and isSuareUpRight)):
                    break

                printLittleSquare(self, [xb, yb])
                x+=1
            y+=1

    def drawErrorLvl(self):
        errorCorrectionLevel = 2
        maskPattern = 2
        formatErrorCorrection = 0 #TODO ?

        self.setPixel(1, 9, (errorCorrectionLevel >> 1) %2 == 1) # draw errorCorrectionLevel.
        self.setPixel(9, self.size-2, (errorCorrectionLevel >> 1) %2 == 1)
        self.setPixel(2, 9, (errorCorrectionLevel >> 0) %2 == 1)
        self.setPixel(9, self.size-3, (errorCorrectionLevel >> 0) %2 == 1)

        self.setPixel(3, 9, (maskPattern >> 2) %2 == 1) # draw maskPattern. TODO ? need to flip extremity bit ?
        self.setPixel(9, self.size-4, (maskPattern >> 2) %2 == 1)
        self.setPixel(4, 9, (maskPattern >> 1) %2 == 1)
        self.setPixel(9, self.size-5, (maskPattern >> 1) %2 == 1)
        self.setPixel(5, 9, (maskPattern >> 0) %2 == 1)
        self.setPixel(9, self.size-6, (maskPattern >> 0) %2 == 1)

        #TODO ? draw formatErrorCorrection.

    # draw the binary encoding (4 first pixels).
    def drawBinaryEncoding(self):
        self.setPixel(self.size-2, self.size-2, (self.binaryEncoding >> 3) %2 == 1)
        self.setPixel(self.size-3, self.size-2, (self.binaryEncoding >> 2) %2 == 1)
        self.setPixel(self.size-2, self.size-3, (self.binaryEncoding >> 1) %2 == 1)
        self.setPixel(self.size-3, self.size-3, (self.binaryEncoding >> 0) %2 == 1)

    # draw the length of raw data (in char).
    def drawLengthData(self):
        lengthData = len(self.data)
        self.setPixel(self.size-2, self.size-4, (lengthData >> 7) %2 == 1)
        self.setPixel(self.size-3, self.size-4, (lengthData >> 6) %2 == 1)
        self.setPixel(self.size-2, self.size-5, (lengthData >> 5) %2 == 1)
        self.setPixel(self.size-3, self.size-5, (lengthData >> 4) %2 == 1)
        self.setPixel(self.size-2, self.size-6, (lengthData >> 3) %2 == 1)
        self.setPixel(self.size-3, self.size-6, (lengthData >> 2) %2 == 1)
        self.setPixel(self.size-2, self.size-7, (lengthData >> 1) %2 == 1)
        self.setPixel(self.size-3, self.size-7, (lengthData >> 0) %2 == 1)

    # draw data.
    def drawData(self, dataBin:list):
        x = self.size-2
        y = self.size-8
        indexChar = 0
        indexBin = 0
        isVerifyFill = False
        while(True):
            if(x == 0): # exit loop when no more pixel valid.
                break

            isXPair = x%2 == 0
            isYGoUp = (x-1)%4 >= 2
            xForMask = (self.size-2) - x

            if(self.getPixel(x, y) == None): # write only if the pixel is empty (else skip). 

                isBlack = True
                if(not isVerifyFill):
                    isBlack = (dataBin[indexChar] >> (7-indexBin)) %2 == 1
                else:
                    isBlack = random.random() < 0.45 # TODO ? fill with verification.

                if(xForMask % self.mask == 0): # reverce pixel for mask.
                    isBlack = not isBlack
                self.setPixel(x, y, isBlack)

                indexBin += 1 # next index data.
                if(indexBin == 8):
                    indexBin = 0
                    indexChar += 1
                    if(indexChar >= len(dataBin)):
                        isVerifyFill = True # finish write data.

            if(isXPair): # next pixel.
                x-=1 # go left.
            else:
                x+=1 # go back right.
                if(isYGoUp):
                    y-=1 # go up.
                    if(y == 0): # out of range.
                        y+=1 # go simple left.
                        x-=2
                else:
                    y+=1 # go down.
                    if(y == self.size-1): # out of range.
                        y-=1 # go simple left.
                        x-=2

    def castDataToQRCode(self):
        if(len(self.data) > 255):
            raise Exception("data to long ! (over 255 char)")

        dataBin = self.dataToBin()
        pixelLengthForPrintData = self.evalPixelLengthForBinData(dataBin)
        self.size = self.evalSizeImgForFitData(pixelLengthForPrintData)

        self.drawBorderWhite() # draw canvas.
        self.drawBorderSquare()
        self.drawAlternetBand()
        self.drawLittleSquare()
        self.drawErrorLvl()

        self.drawBinaryEncoding() # draw binary encoding.
        self.drawLengthData() # draw length data.
        self.drawData(dataBin) # draw data bin.
