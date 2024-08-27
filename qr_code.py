import qrcode
import socket
import os
import webbrowser 
PORT = 8080

hostname = socket.gethostname()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
URL = "http://" + s.getsockname()[0] + ":" + str(PORT)



qr = qrcode.QRCode(version=1, box_size=10, border=4)
qr.add_data(URL)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")

img.save(os.path.join(os.getcwd(),"static","my_qr_code.png"))

webbrowser.open(URL)