import SimpleHTTPServer
import SocketServer
from os import curdir, sep

PRINT_INFOS = True # TODO : récupérer la valeur en fonction d'un argument d'exécution
PORT = 8001
TYPE_HTML = "text/html"
TYPE_JSON = "application/json"
TYPE_JS = "text/javascript"

def safeprint (m) :
    if PRINT_INFOS :
        print m

class DoroServer (SimpleHTTPServer.SimpleHTTPRequestHandler) :

    def getFile (self, name, contentType) :
         f = open(curdir + sep + name)
         self.send_response(200)
         self.send_header("Content-type", contentType)
         self.end_headers()
         self.wfile.write(f.read())
         f.close()
         safeprint("served " + name)

    def do_GET (self) :
        try : # TODO : trouver un module de routage avec gestion des arguments
            if self.path == "/doro" :
                self.getFile("doro.html", TYPE_HTML)

            elif self.path == "/cards" :
                self.getFile("data" + sep + "cards.json", TYPE_JSON)

            elif self.path == "/build/react.min.js" :
                self.getFile("build" + sep + "react.min.js", TYPE_JS)

            elif self.path == "/build/jquery-2.1.3.min.js" :
                self.getFile("build" + sep + "jquery-2.1.3.min.js", TYPE_JS)

            elif self.path == "/build/JSXTransformer.js" :
                self.getFile("build" + sep + "JSXTransformer.js", TYPE_JS)

            elif self.path == "/src/doro.js" :
                self.getFile("src" + sep + "doro.js", TYPE_JS)
         
            else :
                safeprint("wrong path : *" + self.path + "*")
        
        except IOError :
            self.send_error(404, "File not found")
            safeprint("io error")

# end DoroServer

httpd = SocketServer.TCPServer(("", PORT), DoroServer)

safeprint("serving at port " + str(PORT) + " on 127.0.0.1")
httpd.serve_forever()
