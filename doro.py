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
decks = json.load(open("data" + sep + "decks.json"))

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
            "/img":        self.getImg,
            "/favicon":    self.getFavicon,
            "/decks":      self.getDecks,
            "/decks-add":  self.getDecksAdd,
            "/deck-add-card":  self.getDeckAddCard,
            "/deck-drop-card": self.getDeckDropCard
        };
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, 
                                                           client_address, server)

    def makeheaders (self, code, contenttype = None) :
            self.send_response(code)
            if contenttype :
                self.send_header("Content-type", contenttype)
            self.end_headers()
        
    def getJSON (self, j) :
        try :
            self.makeheaders(200, TYPE_JSON)
            self.wfile.write(json.dumps(j))
        except IOError :
            self.send_error(404, "File not found")
            safeprint("io error")

    def saveJSON (self, j, name) :
        f = open(curdir + sep + "data" + sep + name,"w")
        f.write(json.dumps(j))
        f.close()

    def getBiblio (self) : self.getJSON(biblio)
    def getDecks  (self) : self.getJSON(decks)

    def saveBiblio (self) : self.saveJSON(biblio, "bibliotheque.json")
    def saveDecks  (self) : self.saveJSON(decks, "decks.json")
        
    def getDeckAddCard (self, params) :
        deck = params["deck"][0]
        card = params["card"][0]
        
        if not deck in decks["decksSet"]  :
            self.send_error(400, "deck inexistant")
            return
        
        if not card in biblio["cardsSet"] :
            self.send_error(400, "carte inexistante")
            return
        
        if len([c for c in decks["decksSet"][deck]["cards"] if c == card]) == 3 :
            safeprint("deja trois cartes de ce nom dans ce deck")
            return
        
        decks["decksSet"][deck]["nbcards"] += 1
        decks["decksSet"][deck]["cards"].append(card);
        
        self.saveDecks()
        self.getDecks()
        
    def getDeckDropCard (self, params) :
        deck = params["deck"][0]
        index = int(params["index"][0])
        
        if not deck in decks["decksSet"]  :
            self.send_error(400, "deck inexistant")
            return
        print index, " ", len(decks["decksSet"][deck]["cards"])
        if index < 0 or index >= len(decks["decksSet"][deck]["cards"]) :
            self.send_error(400, "index incorrect")
            return;
        
        decks["decksSet"][deck]["nbcards"] -= 1
        del decks["decksSet"][deck]["cards"][index]
        
        self.saveDecks()
        self.getDecks()

    def getDecksAdd (self, param) :
        try :
            name = param["name"][0]
            alias = re.sub(r"[^a-zA-Z0-9_-]+", "", name) 

            if alias in decks["decksSet"] :
                return  

            deck = {"id": decks["nbdecks"], "name": name, "cards": [], "nbcards": 0}
            decks["nbdecks"] += 1
            decks["decksSet"][alias] = deck
            decks["decksList"].append(alias)

            self.saveDecks()
            self.getDecks()
        except :
            self.send_error(400, "Name already taken")
            safeprint("nom deck deja pris")

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
            self.makeheaders(404, TYPE_JSON)
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

    def sendFile (self, f) :
        self.wfile.write(f.read())
        f.close()

    def getImg (self, params) :
        name = params["name"][0]
        path = "data" + sep + "img" + sep + re.sub(r"[^.a-zA-Z0-9_-]+", "", name)
        try :
            f = open(curdir + sep + path, "rb")
            self.makeheaders(200, TYPE_PNG)
            self.sendFile(f)
            safeprint("served " + path) 
        except IOError :
            self.send_error(404, "File not found")
            safeprint("io error")

    def getFavicon (self) :
        try :
            f = open(curdir + sep + "img" + sep + "favicon.png", "rb")
            self.makeheaders(200, TYPE_PNG)
            self.sendFile(f)
            safeprint("served favicon") 
        except IOError :
            self.send_error(404, "File not found")
            safeprint("io error")

    def getFile (self, name, contentType) :
        try :
            f = open(curdir + sep + name)
            self.makeheaders(200, contentType)
            self.sendFile(f)
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

