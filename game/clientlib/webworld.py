from twisted.python import log

from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue
from twisted.internet.defer import DeferredList
from twisted.internet.defer import DeferredSemaphore
from twisted.web.client import getPage

import json

import pygame
from pygame.locals import *
from clientlib.tools import *

from clientlib.pygame_helpers import load_image

class Tile(pygame.sprite.Sprite):

    def __init__(self, tiletype, row, col, sizefactor=20):
        pygame.sprite.Sprite.__init__(self)
        self.tiletype = tiletype
        self.image = 'tile_%s_marked.png' % (self.tiletype,)
        self.cordinates = ((col * sizefactor), (row * sizefactor))

        self.image, self.rect = load_image(self.image, None, (sizefactor, sizefactor))
        self.rect.fit(pygame.Rect(0, 0, 5, 5))
        self.rect.topleft = self.cordinates


def silence(error):
    pass

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
    gfxlist = []
    walk = []
    enemies = []
    towers = []
    update_interval = 0.2
    semaphore = DeferredSemaphore(2)

    def pause(self):
        return getPage(self.server % 'pause')

    def destroy(self):
        getPage(self.server % 'stop').addCallback(lambda _: reactor.stop())

    @inlineCallbacks
    def getMap(self):
        to = self.update_interval
        try:
            page = yield self.semaphore.run(getPage, self.server % "map", timeout=to).addErrback(silence)
        except:
            returnValue(None)
        try:
            tilemap = json.loads(page)['data']
            self.map = tilemap
            self.gfxmap = []
            self.gfxlist = []
            for y, line in enumerate(tilemap):
                newline = []
                for x, tile in enumerate(line):
                    t = Tile(tile, y, x)
                    newline.append(t)
                    self.gfxlist.append(t)
                self.gfxmap.append(newline)
            page = yield getPage(self.server % "walk", timeout=to).addErrback(silence)
            walk = json.loads(page)['data']
            self.walk = walk
            log.msg("getMap finished. walk: %s %s" % (self.server % 'map', walk))
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
