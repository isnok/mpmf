import sys, os
import Queue

import pygame
from pygame.locals import *

#from clientlib.Menu import Menu, MenuItem
from clientlib.tools import *

from math import floor, ceil
from random import randint

from clientlib.pygame_helpers import load_image

class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('simon_front%s.png' % randint(1, 2), scale=(20, 20))
        self.rect.topleft = (x, y)
        self.rect.fit(pygame.Rect(0, 0, 5, 5))

class Tower(pygame.sprite.Sprite):

    def __init__(self, y, x):
        pygame.sprite.Sprite.__init__(self)
        i = randint(1,3)
        self.image, self.rect = load_image('tower%s.png' % i, scale=(20, 20))
        self.rect.topleft = (20*x, 20*y)
        self.rect.fit(pygame.Rect(0, 0, 5, 5))

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from clientlib.webworld import WebWorld

class Player:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.char = "@"

    def __str__(self):
        return self.char

class Play():

    def __init__(self, args=None, debug=False):

        self.args = args
        self.debug = debug

        log.startLogging(sys.stdout)
        from twisted.web.client import HTTPClientFactory
        HTTPClientFactory.noisy = False

        self.world = WebWorld(args)
        self.player = Player(10,10)

    def gameloop(self):

        if self.debug:
            log.msg('ascii play starting.')

        pygame.init()
        pygame.display.set_caption("build towers to survive! | ESC for quit")
        self.screen = pygame.display.set_mode(map(int,self.args.resolution.split('x')))
        self.background = pygame.image.load('assets/bg_1024x768.jpg').convert()

        self.screen.blit(self.background, (0, 0))

        self.world.getMap()
        keygrabbing = LoopingCall(self.handle_keys)
        worldupdates = LoopingCall(self.world.update)
        keygrabbing.start(0.1)
        worldupdates.start(0.1)
        reactor.run()

        pygame.quit()

    def draw_map(self, tilemap=None):
        if tilemap is None:
            tilemap = self.world.gfxmap
        self.screen.blit(self.background, (0, 0))

        s = pygame.sprite.Group()
        s.add(*self.world.gfxlist)
        s.draw(self.screen)

        mktow = lambda t: Tower(t['x'], t['y'])
        pygame.sprite.Group(*map(mktow, self.world.towers)).draw(self.screen)

        if self.world.walk:
            mkene = lambda e: Enemy(*self.pos_to_coord(e))
            pygame.sprite.Group(*map(mkene, self.world.enemies)).draw(self.screen)

        pygame.display.flip()
        pygame.display.update()

    def pos_to_coord(self, enemy):
        pos = enemy['pos']
        walk = self.world.walk

        if len(walk) > ceil(pos):
            x1, y1 = walk[int(floor(pos))]
            x2, y2 = walk[int(ceil(pos))]
            eps = pos - floor(pos)
            x = x1 + (x2 - x1) * eps
            y = y1 + (y2 - y1) * eps
        else:
            x, y = walk[-1]
        return self.screen_transform(x, y)

    def screen_transform(self, x, y):
        return (int(20*y), int(20*x))

    def handle_keys(self):
        try:
            player = self.player
            cnt = 1
            for event in [e for e in pygame.event.get() if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONUP)]:
                if e.type == pygame.MOUSEBUTTONUP:
                    x, y = pygame.mouse.get_pos()
                    yg = x / 20
                    xg = y / 20
                    log.msg("trafo: %s,%s -> %s,%s" % (x,y,xg,yg))
                    self.world.place_tower(xg,yg)
                pressed = pygame.key.get_pressed()
                if   pressed[pygame.K_q]: reactor.stop()
                elif pressed[pygame.K_h]: player.x -= 1
                elif pressed[pygame.K_j]: player.y += 1
                elif pressed[pygame.K_k]: player.y -= 1
                elif pressed[pygame.K_l]: player.x += 1
                elif pressed[pygame.K_y]:
                    player.y -= 1
                    player.x -= 1
                elif pressed[pygame.K_u]:
                    player.y -= 1
                    player.x += 1
                elif pressed[pygame.K_b]:
                    player.y += 1
                    player.x -= 1
                elif pressed[pygame.K_n]:
                    player.y += 1
                    player.x += 1
                elif pressed[pygame.K_p]: self.world.pause()
                elif pressed[pygame.K_x]: self.world.destroy()
                elif pressed[pygame.K_SPACE]: self.world.place_tower(player.y, player.x)
                cnt += 1
            self.draw_map()
        except Exception, ex:
            log.err(ex)
