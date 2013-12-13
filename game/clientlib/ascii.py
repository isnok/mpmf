import os, sys
import curses

from twisted.python import log
from twisted.python.logfile import DailyLogFile
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue
from twisted.internet.defer import DeferredList
from twisted.web.client import getPage
import json

def silence(error):
    pass

class Player:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.char = "@"

    def __str__(self):
        return self.char

class WebWorld:

    def __init__(self, args):
        self.args = args
        self.server = 'http://%s:%s/%s/%%s' % (args.host, args.port, args.game)

    map_gfx = {
        'free': ":",
        'walk': "~",
        'spawn': "$",
        'exit': "*",
        'blocked': "#",
    }

    gfxmap = []
    walk = []
    enemies = []
    update_interval = 0.2

    def translate_tile(self, tile):
        return self.map_gfx[tile]

    def pause(self):
        return getPage(self.server % 'pause')

    def destroy(self):
        getPage(self.server % 'stop').addCallback(lambda _: reactor.stop())

    @inlineCallbacks
    def getMap(self):
        to = self.update_interval/4
        try:
            page = yield getPage(self.server % "map", timeout=to).addErrback(silence)
        except:
            returnValue(None)
        try:
            tilemap = json.loads(page)['data']
            self.map = tilemap
            self.gfxmap = [map(self.translate_tile, line) for line in tilemap]
            page = yield getPage(self.server % "walk", timeout=to).addErrback(silence)
            walk = json.loads(page)['data']
            self.walk = walk
        except:
            pass

    def place_tower(self, y, x):
        action = "place"
        if {'x': y, 'y': x} in self.towers:
            action = 'remove'
        url = self.server % ("towers?%s=%d,%d" % (action, y, x))
        return getPage(url).addErrback(silence)

    def update(self, _=None):
        if not self.walk:
            self.getMap().addErrback(silence)
        return DeferredList([
            self.update_towers(),
            self.update_enemies(),
        ])

    @inlineCallbacks
    def update_towers(self, _=None):
        try:
            page = yield getPage(self.server % "towers", timeout=0.1).addErrback(silence)
            towers = json.loads(page)['data']
            self.towers = towers
        except:
            pass

    @inlineCallbacks
    def update_enemies(self, _=None):
        try:
            page = yield getPage(self.server % "enemies", timeout=0.1)
            enemies = json.loads(page)['data']
            self.enemies = enemies
        except:
            pass

class Play():

    def __init__(self, args=None, debug=False):

        self.args = args
        self.debug = debug

        log.startLogging(DailyLogFile.fromFullPath(args.log))

        self.world = WebWorld(args)
        self.player = Player(10,10)

    def gameloop(self):

        if self.debug:
            print 'ascii play starting.'

        self.screen = curses.initscr()

        # dont echo keystrokes
        curses.noecho()
        # dont require pressing enter
        curses.cbreak()
        # handle special keys
        self.screen.keypad(1)

        begin_x = 23 ; begin_y = 7
        height = 5 ; width = 40
        self.window = curses.newwin(height, width, begin_y, begin_x)
        self.window.nodelay(1)

        self.world.getMap()
        keygrabbing = LoopingCall(self.handle_keys)
        worldupdates = LoopingCall(self.world.update)
        keygrabbing.start(0.11)
        worldupdates.start(0.23)
        reactor.run()

        # restore terminal
        self.screen.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def draw_map(self, tilemap=None):
        if tilemap is None:
            tilemap = self.world.gfxmap
        for y, line in enumerate(tilemap):
            l = "".join(line)
            self.screen.addstr(y, 0, l)
        self.screen.addstr(3, 3, str(len(self.world.enemies)))
        self.screen.addstr(3, 12, str(self.player.x))
        self.screen.addstr(3, 16, str(self.player.y))
        for t in self.world.towers:
            try:
                self.screen.addstr(t['x'], t['y'], "O")
            except:
                pass
        for e in self.world.enemies:
            try:
                at = self.world.walk[int(round(e['pos']))]
                self.screen.addstr(at[0], at[1], "X")
            except:
                pass
        self.screen.addstr(self.player.y, self.player.x, str(self.player))
        self.screen.refresh()
        # move the cursor to the player
        curses.setsyx(self.player.y, self.player.x)
        curses.doupdate()

    def handle_keys(self):
        try:
            player = self.player
            c = self.window.getch()
            cnt = 1
            if   c == ord('q'): reactor.stop()
            elif c == ord('h'): player.x -= 1
            elif c == ord('j'): player.y += 1
            elif c == ord('k'): player.y -= 1
            elif c == ord('l'): player.x += 1
            elif c == ord('y'):
                 player.y -= 1
                 player.x -= 1
            elif c == ord('u'):
                 player.y -= 1
                 player.x += 1
            elif c == ord('b'):
                 player.y += 1
                 player.x -= 1
            elif c == ord('n'):
                 player.y += 1
                 player.x += 1
            elif c == ord('p'): self.world.pause()
            elif c == ord('X'): self.world.destroy()
            elif c == ord(' '): self.world.place_tower(player.y, player.x)
            try:
                self.draw_map()
            except:
                pass
            cnt += 1
            c = self.window.getch()
        except Exception, ex:
            print ex
