# Not sure if this can be used, but not deleting it just in case.
import SimpleHTTPServer
import SocketServer


### Setup a webserver
class WebServer:
    def __init__(self, port=8000):
        self.port = port
        self.httpd = None

    def start(self):
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.httpd = SocketServer.TCPServer(("", self.port), Handler)
        print("serving at port", self.port)
        self.httpd.serve_forever()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
