from Class.QRCodeManager import QRCodeManager


# instancie obj QR code manager.
QR = QRCodeManager()

# set data raw to the instance.
QR.setData("hello, I'm a text on a QR code !")

# cast raw data into QR code image.
QR.castDataToQRCode()

# print the QR code image as PNG on a folder.
QR.saveAsPNG("Documents/QRcodeGenerator/pngGenerated.png")