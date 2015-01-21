#!/usr/bin/python
# -*- coding: utf-8 -*-

import SimpleHTTPServer
import SocketServer
import json
import webbrowser
import re
from os import curdir, sep
from os import listdir
from threading import Thread
from urllib2 import urlopen, HTTPError
from urlparse import urlparse, parse_qs

PRINT_INFOS = True # TODO : récupérer la valeur en fonction d'un argument d'exécution
TYPE_HTML = "text/html"
TYPE_JSON = "application/json"
TYPE_JS = "text/javascript"
TYPE_PNG = "image/png"

def safeprint (m) :
    if PRINT_INFOS :
        print m

biblio = json.load(open("data" + sep + "bibliotheque.json"))

decksPaths = [ f for f in listdir("data" + sep + "decks") if f.endswith(".json") ]
decks = [ json.load(p) for p in decksPaths]

class DoroServer (SimpleHTTPServer.SimpleHTTPRequestHandler) :

    def __init__ (self, request, client_address, server) :
        self.mapRequests = {
            "/doro":       self.getDoro,
            "/biblio":     self.getBiblio,
            "/biblio-add": self.getBiblioAdd,
            "/react":      self.getReact,
            "/jquery":     self.getJQuery,
            "/jsxt":       self.getJSXT,
            "/dorojs":     self.getDoroJS,
            "/close":      self.close,
            "/img":        self.getImg
            }
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, 
                                                           client_address, server)

    def getBiblio (self) : 
        try :
            self.send_response(200)
            self.send_header("Content-type", TYPE_JSON)
            self.end_headers()
            self.wfile.write(json.dumps(biblio))
            #safeprint("served biblio") 
        except IOError :
            self.send_error(404, "File not found")
            safeprint("io error")

    def saveBiblio (self) :
        biblioFile = open("data" + sep + "bibliotheque.json", "w")
        biblioFile.write(json.dumps(biblio))
        biblioFile.close()
        
    def getBiblioAdd (self, param) :
        try :
            url = param["url"][0]
            print "*", url, "*"
            req = urlopen(url)
            if not req.geturl().startswith("http://yugioh.wikia.com/wiki/") :
                safeprint("not good site")
                return
            html = req.read()
            
            tableCardPattern = "<table class=\"cardtable\">"
            imgPattern = "<td class=\"cardtable-cardimage\" rowspan=\"91\"><a href=\""
            englishPattern = "scope=\"row\">English</th>"

            tableCardStart = html.find(tableCardPattern)
            if tableCardStart == -1 :
                print "not a card"
                return

            imgStart = html.find(imgPattern, tableCardStart) + len(imgPattern)
            imgEnd = html.find("\"", imgStart)

            englishStart = html.find(englishPattern, imgEnd) + len(englishPattern)
            englishEnd = html.find(" style=\";\"", englishStart)

            nameStart = html.find(">", englishEnd) + 2
            nameEnd = html.find("<", nameStart)

            img = html[imgStart:imgEnd]
            name = html[nameStart:nameEnd]
            alias = re.sub(r"[^a-zA-Z0-9_-]+", "", name)   
         
            if alias in biblio["cardsSet"] :
                print "already here"
                return

            imgFile = open("data" + sep + "img" + sep + alias + ".png", "w")
            imgFile.write(urlopen(img).read())
            imgFile.close()
            
            card = {"id": biblio["nbcards"], "name": name, "imgExt": "png", "url": url}
            biblio["nbcards"] += 1
            biblio["cardsSet"][alias] = card
            biblio["cardsList"].append(alias)
           
            self.saveBiblio()
            self.getBiblio()

        except HTTPError :
            self.send_response(404)
            self.send_header("Content-type", TYPE_JSON)
            self.end_headers()
            self.wfile.write("{\"success\": false}")
            safeprint("url asked not found")

    def getDoro (self)   : self.getFile("doro.html", TYPE_HTML)
    def getCards (self)  : self.getBiblio()
    def getReact (self)  : self.getFile("build" + sep + "react.js", TYPE_JS)
    def getJQuery (self) : self.getFile("build" + sep + "jquery-2.1.3.min.js", TYPE_JS)
    def getJSXT (self)   : self.getFile("build" + sep + "JSXTransformer.js", TYPE_JS)
    def getDoroJS (self) : self.getFile("src" + sep + "doro.js", TYPE_JS)
    def close (self) :
        closer = Thread(target = self.server.shutdown)
        closer.daemon = True
        closer.start()

    def getImg (self, params) :
        name = params["name"][0]
        path = "data" + sep + "img" + sep + re.sub(r"[^.a-zA-Z0-9_-]+", "", name)
        try :
            f = open(curdir + sep + path, "rb")
            self.send_response(200)
            self.send_header("Content-type", TYPE_PNG)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            safeprint("served " + path) 
        except IOError :
            self.send_error(404, "File not found")
            safeprint("io error")


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
        req = urlparse(self.path)
        args = parse_qs(req.query)
        
        if len(args) :
            self.mapRequests[req.path](args)
        else :
            self.mapRequests[req.path]()

        
# end DoroServer

httpd = SocketServer.TCPServer(("", 0), DoroServer)
_, port =  httpd.socket.getsockname()
safeprint("serving at port " + str(port) + " on 127.0.0.1")
webbrowser.open_new_tab("http://127.0.0.1:" + str(port) + "/doro")

try :
    httpd.serve_forever()
except KeyboardInterrupt :
    httpd.shutdown()

