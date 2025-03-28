from Class.GreyImgManager import GreyImgManager
import numpy as np
import reedsolo

# doc use : https://youtu.be/s4Qo0g-bgMY?si=ehuFZPE437iquP1b (The Unqualified Tutor)
# doc use : https://youtu.be/w5ebcowAJD8?si=pwwYsXoTy7m7CjI0 (Veritasium)
# doc use : https://en.wikipedia.org/wiki/QR_code (Wiki)
# doc use : https://youtu.be/142TGhaTMtI?si=bR5N2oarf-P0et26 (James Explains)

# obj QRCodeManager make an img QR code from a string data.
class QRCodeManager(GreyImgManager):
    def __init__(self):
        super().__init__()
        self.data = "" # raw data.
        self.mask = 7 # mask patern default 7 (between 0 to 7).
        self.binaryEncoding = 4 # binary encoding default 4 (1:numeric, 2:alphanumeric, 4:binary, 8:japanese kanji) (only 4 implemented).
        self.errorCorrectionLevel = 3 # level of correction error default 3 (3:Low 7%, 2:Medium 15%, 1:Quartile 25%, 0:High 30%) (only 3 implemented)
        self.size = None # width of img QR code (include white border).
        self.errorCorrectionLength = 7 # amount of block byte allow for correction (default 7).
        
    # overide setPixel by sending bool (true = black).
    def setPixel(self, x:int, y:int, pixelValue:bool):
        super().setPixel(x, y, 0 if pixelValue else 255)

    # set data.
    def setData(self, data:str):
        self.data = data

    # cast raw data into a list of int (0 to 255).
    def castDataToBin(self):
        return list(map(lambda c: ord(c), self.data))
    
    # return a list of int (0 to 255) including error correction data.
    def evalErrorCorrectionBinData(self, dataBin:list):

        #a = 2
        #
        #def p(dataBin:list, x:int):
        #    out = 0
        #    for i in range(len(dataBin)):
        #        out += dataBin[i] * pow(x, i)
        #    return out
        #
        #def g(x:int, a:int, errorCorrectionLength:int):
        #    out = 1
        #    for i in range(errorCorrectionLength):
        #        out *= x - pow(a, i)
        #    return out
        #
        ##def r(x:int, rr:list):
        ##    out = 0
        ##    for i in range(len(rr)):
        ##        out += rr[i] * pow(x, i)
        #
        #rr = []
        #for i in range(self.errorCorrectionLength):
        #    #pg = p(dataBin, i) % g(i, a, self.errorCorrectionLength)
        #    gResult = g(i, a, self.errorCorrectionLength)
        #    pg = p(dataBin, i)
        #    if(gResult != 0):
        #        pg %= gResult
        #    for j in range(len(rr)):
        #        pg -= rr[j] * pow(i, j)
        #    pg /= pow(i, i)
        #    rr.append(int(pg))
        #
        #print("error correction calculated :")
        #print(rr)
        #
        #return rr

        bitList = reedsolo.RSCodec(self.errorCorrectionLength).encode(dataBin)
        dataFull = []
        for b in bitList:
            char = 0
            for i in range(8):
                char += (1 << i) if (b >> i) %2 == 1 else 0
            dataFull.append(char)

        return dataFull


    # try many size of QR code, until find the good size to fit data.
    def evalSizeImgForFitData(self):
        dataLenPix = len(self.data) *8 # amount of pixel need to print the data raw.

        sizeFormat = 1
        while(True):
            size = 9*2 +1 +(4*sizeFormat)

            amountLS = None # eval the amount of little square.
            pixBusyByLS = None # eval the amount of pixel busy by little square.
            if(sizeFormat == 1):
                amountLS = 0
                pixBusyByLS = 0
            elif(sizeFormat < 7):
                amountLS = 1
                pixBusyByLS = 25
            elif(sizeFormat < 11):
                amountLS = 6
                pixBusyByLS = 4*25 + 2*20
            else:
                raise Exception("Qr code to big, vertion 11 and more not implemented")

            lengthPixelCanBeUse = (sizeFormat *4 *8 *2) + pow(size - 11, 2) # eval pixel can be used.
            lengthPixelCanBeUse -= pixBusyByLS
            lengthPixelCanBeUse -= 4 +8 # use to info data.
            lengthPixelCanBeUse -= lengthPixelCanBeUse %8

            if(self.errorCorrectionLength == None): # return if correction length is none.
                if(lengthPixelCanBeUse >= dataLenPix + 7*8):
                    self.errorCorrectionLength = int((lengthPixelCanBeUse - dataLenPix) /8)
                    return size
            elif(lengthPixelCanBeUse >= dataLenPix + self.errorCorrectionLength *8):
                return size

            sizeFormat += 1

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

    # draw the pixel black (only the same at this pos).
    def drawFixedBlackPixel(self):
        self.setPixel(9, self.size-9, True)

    # draw every little square.
    def drawLittleSquare(self):
        def printLittleSquare(QR, pos):
            for x in range(5):
                for y in range(5):
                    xb = 2-abs(x-2)
                    yb = 2-abs(y-2)
                    isBlack = min(xb,yb)%2 == 0
                    QR.setPixel(x+pos[0], y+pos[1], isBlack)

        sizeFormat = int((self.size -9*2 -1) /4)
        if(sizeFormat == 1):
            return
        elif(sizeFormat < 7):
            printLittleSquare(self, [self.size-10, self.size-10])
        elif(sizeFormat < 11):
            posStart = [self.size-10, self.size-10]
            spacingLS = int((self.size -5*2 -5) /2)
            printLittleSquare(self, [posStart[0] -spacingLS*0, posStart[1] -spacingLS*0])
            printLittleSquare(self, [posStart[0] -spacingLS*1, posStart[1] -spacingLS*0])
            printLittleSquare(self, [posStart[0] -spacingLS*0, posStart[1] -spacingLS*1])
            printLittleSquare(self, [posStart[0] -spacingLS*1, posStart[1] -spacingLS*1])
            printLittleSquare(self, [posStart[0] -spacingLS*2, posStart[1] -spacingLS*1])
            printLittleSquare(self, [posStart[0] -spacingLS*1, posStart[1] -spacingLS*2])
        else:
            raise Exception("Qr code to big, vertion 11 and more not implemented")

    # draw error correction level.
    def drawErrorCorrectionLevel(self):
        self.setPixel(1, 9, (self.errorCorrectionLevel >> 1) %2 == 1) # draw errorCorrectionLevel.
        self.setPixel(9, self.size-2, (self.errorCorrectionLevel >> 1) %2 == 1)
        self.setPixel(2, 9, (self.errorCorrectionLevel >> 0) %2 == 1)
        self.setPixel(9, self.size-3, (self.errorCorrectionLevel >> 0) %2 == 1)

    # draw mask pattern.
    def drawMaskPattern(self):
        self.setPixel(3, 9, (self.mask >> 2) %2 == 1) # draw maskPattern.
        self.setPixel(9, self.size-4, (self.mask >> 2) %2 == 1)
        self.setPixel(4, 9, (self.mask >> 1) %2 == 1)
        self.setPixel(9, self.size-5, (self.mask >> 1) %2 == 1)
        self.setPixel(5, 9, (self.mask >> 0) %2 == 1)
        self.setPixel(9, self.size-6, (self.mask >> 0) %2 == 1)

    # draw format error correction.
    def drawFormatErrorCorrection(self):
        errorCorrection = 2+8+32+128+256 #TODO edit depend on EClevel and mask, now hardcoded for 3 and 7.
        
        self.setPixel(6, 9, (errorCorrection >> 9) %2 == 1)
        self.setPixel(9, self.size-7, (errorCorrection >> 9) %2 == 1)
        self.setPixel(8, 9, (errorCorrection >> 8) %2 == 1)
        self.setPixel(9, self.size-8, (errorCorrection >> 8) %2 == 1)
        self.setPixel(9, 9, (errorCorrection >> 7) %2 == 1)
        self.setPixel(self.size-9, 9, (errorCorrection >> 7) %2 == 1)
        self.setPixel(9, 8, (errorCorrection >> 6) %2 == 1)
        self.setPixel(self.size-8, 9, (errorCorrection >> 6) %2 == 1)
        self.setPixel(9, 6, (errorCorrection >> 5) %2 == 1)
        self.setPixel(self.size-7, 9, (errorCorrection >> 5) %2 == 1)
        self.setPixel(9, 5, (errorCorrection >> 4) %2 == 1)
        self.setPixel(self.size-6, 9, (errorCorrection >> 4) %2 == 1)
        self.setPixel(9, 4, (errorCorrection >> 3) %2 == 1)
        self.setPixel(self.size-5, 9, (errorCorrection >> 3) %2 == 1)
        self.setPixel(9, 3, (errorCorrection >> 2) %2 == 1)
        self.setPixel(self.size-4, 9, (errorCorrection >> 2) %2 == 1)
        self.setPixel(9, 2, (errorCorrection >> 1) %2 == 1)
        self.setPixel(self.size-3, 9, (errorCorrection >> 1) %2 == 1)
        self.setPixel(9, 1, (errorCorrection >> 0) %2 == 1)
        self.setPixel(self.size-2, 9, (errorCorrection >> 0) %2 == 1)

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

    # apply mask on a pixel.
    def applyMaskOnAPixel(self, j:int, i:int, isBlack:bool):
        if(self.mask == 0):
            return not isBlack if ((i*j)%2 + (i*j)%3 == 0) else isBlack
        if(self.mask == 1):
            return not isBlack if ((int(i/2) + int(j/3))%2 == 0) else isBlack
        if(self.mask == 2):
            return not isBlack if (((i*j)%3 +i +j)%2 == 0) else isBlack
        if(self.mask == 3):
            return not isBlack if (((i*j)%3 + i*j)%2 == 0) else isBlack
        if(self.mask == 4):
            return not isBlack if (i%2 == 0) else isBlack
        if(self.mask == 5):
            return not isBlack if ((i+j)%2 == 0) else isBlack
        if(self.mask == 6):
            return not isBlack if ((i+j)%3 == 0) else isBlack
        if(self.mask == 7):
            return not isBlack if (j%3 == 0) else isBlack
        raise Exception("mask unknow !")

    # draw data.
    def drawData(self, dataBin:list, dataBinCript:list):
        x = self.size-2
        y = self.size-8
        indexChar = 0
        indexBin = 0
        isEnddataBin = False
        fourZero = 4
        charBinCapacity = (17 - len(dataBin)) *8
        enFillValues = [255-3-16, 16+1]
        while(True):
            if(x == 0): # exit loop when no more pixel valid.
                break

            isXPair = x%2 == 0
            isYGoUp = (x-1)%4 >= 2

            if(self.getPixel(x, y) == None): # write only if the pixel is empty (else skip). 

                isBlack = False
                if(isEnddataBin):
                    if(fourZero > 0):
                        fourZero -= 1
                        if(fourZero == 0):
                            indexChar = 0
                            indexBin = 0
                    elif(charBinCapacity > 0):
                        charBinCapacity -= 1
                        if(charBinCapacity == 0):
                            indexChar = 0
                            indexBin = 0
                        isBlack = (enFillValues[indexChar %2] >> (7-indexBin)) %2 == 1
                    else:
                        isBlack = (dataBinCript[indexChar] >> (7-indexBin)) %2 == 1
                else:
                    isBlack = (dataBin[indexChar] >> (7-indexBin)) %2 == 1
                isBlack = self.applyMaskOnAPixel(x-1, y-1, isBlack) # reverce pixel for mask.
                self.setPixel(x, y, isBlack)

                indexBin += 1 # next index data.
                if(indexBin == 8):
                    indexBin = 0
                    indexChar += 1
                    if(indexChar >= len(dataBin) and not isEnddataBin):
                        indexBin = 0
                        indexChar = 0
                        isEnddataBin = True # finish write data.

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

        dataBin = self.castDataToBin() # eval data on a list of int (0~255)
        self.size = self.evalSizeImgForFitData() # eval size QR code for data.
        dataBinCript = self.evalErrorCorrectionBinData(dataBin) # add error byte correction.

        self.drawBorderWhite() # draw canvas.
        self.drawBorderSquare()
        self.drawAlternetBand()
        self.drawFixedBlackPixel()
        self.drawLittleSquare()
        self.drawErrorCorrectionLevel()
        self.drawMaskPattern()
        self.drawFormatErrorCorrection()

        self.drawBinaryEncoding() # draw binary encoding.
        self.drawLengthData() # draw length data.
        self.drawData(dataBin, dataBinCript) # draw data bin.
