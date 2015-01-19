#!/usr/bin/python
# -*- coding: utf-8 -*-

import SimpleHTTPServer
import SocketServer
import json
from os import curdir, sep
from build.urltree import URLTree
from os import listdir

PRINT_INFOS = True # TODO : récupérer la valeur en fonction d'un argument d'exécution
PORT = 8001
TYPE_HTML = "text/html"
TYPE_JSON = "application/json"
TYPE_JS = "text/javascript"

def safeprint (m) :
    if PRINT_INFOS :
        print m

class DoroServer (SimpleHTTPServer.SimpleHTTPRequestHandler) :

    def __init__ (self, request, client_address, server) :
        self.biblio = json.load(open("data" + sep + "bibliotheque.json"))
        decksPaths = [ f for f in listdir("data" + sep + "decks") if f.endswith(".json") ]
        self.decks = [ json.load(p) for p in decksPaths]
        self.mapper = URLTree()
        self.mapper.route("/doro", self.getDoro, "get")
        self.mapper.route("/biblio", self.getCards, "get")
        self.mapper.route("/react", self.getReact, "get")
        self.mapper.route("/jquery", self.getJQuery, "get")
        self.mapper.route("/jsxt", self.getJSXT, "get")
        self.mapper.route("/dorojs", self.getDoroJS, "get")
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)

    def getBiblio (self) : 
        try :
            self.send_response(200)
            self.send_header("Content-type", TYPE_JSON)
            self.end_headers()
            json.dumps(self.biblio)
            safeprint("served biblio") 
        except IOError :
            self.send_error(404, "File not found")
            safeprint("io error")

    def getDoro (self)   : self.getFile("doro.html", TYPE_HTML)
    def getCards (self)  : self.getBiblio()
    def getReact (self)  : self.getFile("build" + sep + "react.js", TYPE_JS)
    def getJQuery (self) : self.getFile("build" + sep + "jquery-2.1.3.min.js", TYPE_JS)
    def getJSXT (self)   : self.getFile("build" + sep + "JSXTransformer.js", TYPE_JS)
    def getDoroJS (self) : self.getFile("src" + sep + "doro.js", TYPE_JS)

    def getFile (self, name, contentType) :
        try :
            f = open(curdir + sep + name)
            self.send_response(200)
            self.send_header("Content-type", contentType)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            safeprint("served " + name) 
        except IOError :
            self.send_error(404, "File not found")
            safeprint("io error")

    def do_GET (self) :
        method, params = self.mapper.resolve("get", self.path)
        if method is not None :
            method()
        else :
            safeprint("wrong path : *" + self.path + "*")
        
# end DoroServer

httpd = SocketServer.TCPServer(("", PORT), DoroServer)

safeprint("serving at port " + str(PORT) + " on 127.0.0.1")
try :
    while True :
        httpd.handle_request()
except KeyboardInterrupt :
    try : httpd.shutdown()
    except Exception :
        pass
