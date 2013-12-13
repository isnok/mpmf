import pygame
from pygame.locals import *

from twisted.python import log
from ClientLib.pygame_sdl.PygameBase import BaseSDLGame
from ClientLib.Interfaces import IWebWorld

#from zope.interface import implements
from zope.interface import classProvides
from twisted.plugin import IPlugin
from ClientLib.Interfaces import ISDLFrontend

from ClientLib.pygame_sdl.helpers import load_image

class TileSprite(pygame.sprite.Sprite):

    def __init__(self, desc, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('tile_%s.png' % desc, scale=(20,20))
        self.rect.topleft = pos

class TowerSprite(pygame.sprite.Sprite):

    def __init__(self, data):
        pygame.sprite.Sprite.__init__(self)
        x = data['y']
        y = data['x']
        self.image, self.rect = load_image('tower1.png', scale=(20, 20))
        self.rect.topleft = (20*(x+1), 20*(y+1))

from math import ceil
from math import floor

class EnemySprite(pygame.sprite.Sprite):

    def __init__(self, data, walk):
        pygame.sprite.Sprite.__init__(self)
        x, y = self.pos_to_coord(data['pos'], walk)
        self.image, self.rect = load_image('simon_front1.png', scale=(20, 20))
        self.rect.topleft = (x,y)

    def pos_to_coord(self, pos, walk):
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
        pos = (int(20*(y+1)), int(20*(x+1)))
        return pos

class SimpleTDClientSDL(BaseSDLGame):

    plays = 'SimpleTD'
    classProvides(IPlugin, ISDLFrontend)

    def startUp(self):
        self.games = {}
        pygame.display.set_caption("Play SimpleTD! ESC or q to quit")
        self.screen = pygame.display.set_mode((1024,768))
        self.background = pygame.image.load('assets/starfield_background-1024x770.png').convert()
        self.screen.blit(self.background, (0, 0))

        self.font = pygame.font.SysFont("monospace", 35)
        text = self.font.render("SimpleTD!", 1, (255,255,0), (0,0,255))
        self.screen.blit(text, (100, 100))
        self.world_tiles = None
        IWebWorld(5).update({'static': 'true'})

    def update(self, data):
        data = data['data']
        if 'map' in data:
            self.init_map(data['map'])
            self.walk = data['walk']
        if not self.world_tiles:
            return
        self.towers = pygame.sprite.Group(*map(TowerSprite, data['towers']))
        enemies = []
        for ene in data['enemies']:
            enemies.append(EnemySprite(ene, self.walk))
        self.enemies = pygame.sprite.Group(*enemies)
        self.draw_map()
        pygame.display.flip()
        pygame.display.update()

    def init_map(self, mapdata):
        #control = []
        self.world_tiles = pygame.sprite.Group()
        for y, row in enumerate(mapdata):
            line = ''
            for x, desc in enumerate(row):
                line += desc[0]
                pos = (20*(x+1), 20*(y+1))
                self.world_tiles.add(TileSprite(desc, pos))
            #control.append(line)
        #control = "\n".join(control)
        #log.msg("Check:\n%s" % control)

    def draw_map(self, tilemap=None):
        self.world_tiles.draw(self.screen)
        self.towers.draw(self.screen)
        self.enemies.draw(self.screen)
        pygame.display.flip()
        pygame.display.update()

    def onClick(self, coord):
        x, y = coord
        yg, xg = x/20, y/20
        arg = '%d,%d' % (xg-1,yg-1)
        log.msg("click: %s,%s -> %s" % (x,y,arg))
        return IWebWorld(5).update({'place': arg})
