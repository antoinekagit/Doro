import SimpleHTTPServer
import SocketServer
from os import curdir, sep

PORT = 8001

class DoroServer (SimpleHTTPServer.SimpleHTTPRequestHandler) :
    def getFile (self, contentType) :
         f = open(curdir + sep + "doro.html")
         self.send_response(200)
         self.send_header("Content-type", "text/html")
         self.end_headers()
         self.wfile.write(f.read())
         f.close()
         print "served doro html"
    def do_GET (self) :
        try :
            if self.path is "/" :
                f = open(curdir + sep + "doro.html")
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                print "served doro html"
                return
            elif self.path is "cards.json" :
                f = open(curdir + sep + "cards.json")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                print "served json"
                return
            else :
                print "wrong path"
        except IOError :
            self.send_error(404, "File not found")
            print "io error"
        return

httpd = SocketServer.TCPServer(("", PORT), DoroServer)

print "serving at port", PORT
httpd.serve_forever()
