#!/usr/bin/python
# -*- coding: utf-8 -*-

import SimpleHTTPServer
import SocketServer
import json
import webbrowser
import re
from os import curdir, sep, remove, listdir
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

d = {
    "biblio": json.load(open("data" + sep + "bibliotheque.json")),
    "decks":  json.load(open("data" + sep + "decks.json"))
}

class DoroServer (SimpleHTTPServer.SimpleHTTPRequestHandler) :

    def __init__ (self, request, client_address, server) :
        self.mapRequests = {
            "/doro":       self.getDoroHTML,
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
            "/deck-drop-card": self.getDeckDropCard,
            "/deck-del":   self.getDeckDel,
            "/data":       self.getData,
            "/card-del":   self.getCardDel
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

    def saveJSON (self, j, name) :
        f = open(curdir + sep + "data" + sep + name,"w")
        f.write(json.dumps(j, sort_keys=True, indent=4, separators=(',', ': ')))
        f.close()

    def getBiblio (self) : self.getJSON(d["biblio"])
    def getDecks  (self) : self.getJSON(d["decks"])
    def getData   (self) : self.getJSON(d) 

    def saveBiblio (self) : self.saveJSON(d["biblio"], "bibliotheque.json")
    def saveDecks  (self) : self.saveJSON(d["decks"], "decks.json")
    def saveData   (self) : 
        self.saveBiblio()
        self.saveDecks()

    def getCardDel (self, params) :
        cardAlias = params["card"][0]
        
        if not cardAlias in d["biblio"]["set"] :
            self.send_errors(400, "carte inexistante")

        remove(curdir + sep + "data" + sep + "img" + sep + 
               cardAlias + "." + d["biblio"]["set"][cardAlias]["imgExt"])

        d["biblio"]["nb"] -= 1
        del d["biblio"]["set"][cardAlias]

        for i in d["biblio"]["lists"] :
            try : d["biblio"]["lists"][i].remove(cardAlias)
            except ValueError : pass

        for i in d["decks"]["set"] :
            while True :
                try : 
                    d["decks"]["set"][i]["cards"].remove(cardAlias)
                    d["decks"]["set"][i]["nbcards"] -= 1
                except ValueError : 
                    safeprint("yo")
                    break

        self.saveData()
        self.getData()

    def getDeckDel (self, params) :
        deckAlias = params["deck"][0]

        if not deckAlias in d["decks"]["set"] :
            self.send_erros(400, "deck inexistant")

        d["decks"]["nb"] -= 1
        del d["decks"]["set"][deckAlias]
        del d["decks"]["list"][ d["decks"]["list"].index(deckAlias) ]

        self.getDecks()
        self.saveDecks()

    def getDeckAddCard (self, params) :
        deck = params["deck"][0]
        card = params["card"][0]
        
        if not deck in d["decks"]["set"]  :
            self.send_error(400, "deck inexistant")
            return
        
        if not card in d["biblio"]["set"] :
            self.send_error(400, "carte inexistante")
            return
        
        if d["decks"]["set"][deck]["cards"].count(card) == 3 :
            self.send_error(400, "deja trois cartes de ce nom dans ce deck")
            return
        
        d["decks"]["set"][deck]["nbcards"] += 1
        d["decks"]["set"][deck]["cards"].append(card);
        
        self.saveDecks()
        self.getDecks()
        
    def getDeckDropCard (self, params) :
        deck = params["deck"][0]
        index = int(params["index"][0])
        
        if not deck in d["decks"]["set"]  :
            self.send_error(400, "deck inexistant")
            return

        if index < 0 or index >= len(d["decks"]["set"][deck]["cards"]) :
            self.send_error(400, "index incorrect")
            return;
        
        d["decks"]["set"][deck]["nbcards"] -= 1
        del d["decks"]["set"][deck]["cards"][index]
        
        self.getDecks()
        self.saveDecks()

    def getDecksAdd (self, param) :
        try :
            name = param["name"][0]
            alias = re.sub(r"[^a-zA-Z0-9_-]+", "", name) 

            if alias in d["decks"]["set"] :
                return  

            deck = {"name": name, "cards": [], "nbcards": 0}
            d["decks"]["nb"] += 1
            d["decks"]["set"][alias] = deck
            d["decks"]["list"].append(alias)

            self.saveDecks()
            self.getDecks()

        except :
            self.send_error(400, "nom déjà pris")

    def getBiblioAdd (self, param) :
        try :
            url = param["url"][0]

            req = urlopen(url)
            if not req.geturl().startswith("http://yugioh.wikia.com/wiki/") :
                self.send_error(400, "mauvais site")
                return
            html = req.read()
            
            tableCardPattern = "<table class=\"cardtable\">"
            imgPattern = "<td class=\"cardtable-cardimage\" rowspan=\"91\"><a href=\""
            englishPattern = "scope=\"row\">English</th>"
            typesPattern = "Type"
            typesPattern2 = "<td id=\"\" class=\"cardtablerowdata\" style=\";\">"

            tableCardStart = html.find(tableCardPattern)
            if tableCardStart == -1 :
                self.send_error(400, "pas une carte")
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
            types = []

            typesStart = html.find(typesPattern, nameEnd) + len(typesPattern)
            typesStart2 = html.find(typesPattern2, typesStart) + len(typesPattern2) + 1
            typeStart = html.find("<a", typesStart2, typesStart2 + 2) + 2

            while typeStart != -1 :
                typeStart = html.find(">", typeStart) + 1
                typeEnd = html.find("</a>", typeStart)
                types.append(html[typeStart:typeEnd])
                typeStart = html.find("/<a", typeEnd + 4, typeEnd + 7)

            print types

            if alias in d["biblio"]["set"] :
                self.send_error(400, "déjà dans la bibliothèque")
                return

            imgFile = open("data" + sep + "img" + sep + alias + ".png", "w")
            imgFile.write(urlopen(img).read())
            imgFile.close()
            
            card = {"name": name, "types": types, "imgExt": "png", "url": url}
            d["biblio"]["nb"] += 1
            d["biblio"]["set"][alias] = card
            d["biblio"]["lists"]["ajout"].append(alias)
            
            if "Trap Card" in types :
                d["biblio"]["lists"]["trap"].append(alias)
            elif "Spell Card" in types :
                d["biblio"]["lists"]["magic"].append(alias)
            else :
                d["biblio"]["lists"]["monster"].append(alias)

            d["biblio"]["lists"]["all"] = d["biblio"]["lists"]["monster"] + d["biblio"]["lists"]["magic"] + d["biblio"]["lists"]["trap"]

            self.saveBiblio()
            self.getBiblio()

        except HTTPError :
            self.send_error(404, "file not found")

    def getDoroHTML (self)   : self.getFile("src" + sep + "doro.html", TYPE_HTML)
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
        except IOError :
            self.send_error(404, "File not found")

    def getFavicon (self) :
        try :
            f = open(curdir + sep + "img" + sep + "favicon.png", "rb")
            self.makeheaders(200, TYPE_PNG)
            self.sendFile(f)
        except IOError :
            self.send_error(404, "File not found")

    def getFile (self, name, contentType) :
        try :
            f = open(curdir + sep + name)
            self.makeheaders(200, contentType)
            self.sendFile(f)
        except IOError :
            self.send_error(404, "File not found")

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

