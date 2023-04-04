import os
from random import randint

import eel
import http.server
import socketserver
import os
import qrcode


# Generate a QR code with the local host URL
url = 'http://localhost:8000'
img = qrcode.make(url)

# Save the QR code image to a file
img.save('qrcode.png')

# Define the web server handler
handler = http.server.SimpleHTTPRequestHandler

# Start the web server on port 8000
with socketserver.TCPServer(("", 8000), handler) as httpd:
    print("Server started at http://localhost:8000")
    # Wait for incoming connections
    httpd.serve_forever()


dirname = os.path.dirname(__file__)
eel.init(dirname + "/web/")


# Exposing the random_python function to javascript
@eel.expose
def random_python():
    print("Random function running")
    return randint(1, 100)


eel.start("index.html", mode="firefox")
