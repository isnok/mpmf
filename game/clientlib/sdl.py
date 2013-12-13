
import sys, os
import Queue

import pygame
from pygame.locals import *

#from clientlib.Menu import Menu, MenuItem
from clientlib.tools import *

from math import floor, ceil
from random import randint

class Map():

    def __init__(self, debug=False, sizefactor=None):
        self.debug = debug
        self.tiles = {'free': [], 'walk': [], 'spawn': [], 'exit': [], 'blocked': []}
        self.col_max = 0
        self.sizefactor = sizefactor
        self.map = None

    def __repr__(self):
        return repr(self.get_map('ascii', colors=True))

    def set_map(self, json):
        self.map = json

    def get_map(self, style='ascii', colors=True):
        map = ''
        if style == 'ascii':
            for row in self.map:
                for tile in row:
                    if colors:
                        color_tile = tile[0]
                        color_tile = color_tile.replace('f', color(' ', bgcolor='green'))
                        color_tile = color_tile.replace('w', color(' ', bgcolor='white'))
                        color_tile = color_tile.replace('s', color(' ', bgcolor='blue'))
                        color_tile = color_tile.replace('e', color(' ', bgcolor='red'))
                        color_tile = color_tile.replace('b', color(' ', bgcolor='black'))
                        map += color_tile
                    else:
                        map += tile[0]
                map += '\n'
        else:
            output('unknown map visualisation style', 'error')

        return map

    def build_map(self):
        row_cnt = 0
        self.col_max = 0
        for row in self.map:
            col_cnt = 0
            row_cnt += 1

            for tile in row:
                col_cnt += 1

                if tile in self.tiles.keys():
                    self.tiles[tile].append(Tile(tile, row_cnt, col_cnt, self.sizefactor))
                else:
                    output('Unknown string in Map: %s/' % tile, 'error')

            if self.col_max < col_cnt:
                self.col_max = col_cnt

        if self.debug:
            self.infos()

    def infos(self):
        print
        print "RENDERING MAP"
        print "map size: %sx%s" % (len(self.map),len(self.map[0]),)
        print "max row size: %s" % (self.col_max, )
        print "%s free tiles" % (len(self.tiles['free']),)
        print "%s way tiles" % (len(self.tiles['walk']),)
        print "%s blocked tiles" % (len(self.tiles['blocked']),)
        print "%s entries" % (len(self.tiles['spawn']),)
        print "%s exits" % (len(self.tiles['exit']),)
        print self.get_map('ascii', colors=True)

class Tile(pygame.sprite.Sprite):

    def __init__(self, tiletype, row, col, sizefactor=None):
        pygame.sprite.Sprite.__init__(self)
        self.tiletype = tiletype
        self.image = 'tile_%s_marked.png' % (self.tiletype,)
        self.cordinates = ((col * sizefactor), (row * sizefactor))

        self.image, self.rect = load_image(self.image, None, (sizefactor, sizefactor))
        self.rect.fit(pygame.Rect(0, 0, 5, 5))
        self.rect.topleft = self.cordinates

class Enemy(pygame.sprite.Sprite):

    def __init__(self, name, hp, speed, startpoint=(0, 0), style=None, sizefactor=None):
        pygame.sprite.Sprite.__init__(self)

        self.name = name
        self.hp = hp
        self.speed = speed
        self.image, self.rect = load_image('simon_front%s.png' % randint(1, 2), 0, (sizefactor, sizefactor))
        self.rect.topleft = startpoint

class Tower(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image('tower%s.png' % randint(1, 3))
        self.rect.center = (x, y)

class Play():

    def __init__(self, queue=None, commands=None, args=None, debug=False):
        self.queue = queue
        self.commands = commands
        self.debug = debug
        self.fps = 30
        self.sizefactor = None
        self.caption = 'kill them all'
        self.menus = {
            'start': ['Start Game', 'Settings', 'Quit'],
            'pause': ['Continue', 'Settings', 'Quit'],
        }

        self.walk = self.enemies = self.towers = []
        self.rendered = {}

        if args is not None:
            self.resolution = (int(args.resolution.split('x')[0]), int(args.resolution.split('x')[1]))
            self.position = (int(args.coordinates.split('x')[0]), int(args.coordinates.split('x')[1]))
        else:
            self.resolution = (1024, 768)
            self.position = (0, 0)
        self.sizefactor = self.get_sizefactor(self.sizefactor)
        output('sizefactor: %s' % self.sizefactor, 'debug', source='Play().__init__()')

        if args.fullscreen:
            pygame.display.toggle_fullscreen()

        self.map = Map(self.debug, self.sizefactor)

        os.environ['SDL_VIDEO_WINDOW_POS'] = '%s,%s' % self.position

        if not pygame.font:
            output('No Fonts found', 'error', source='Play().__init__()')

    def get_sizefactor(self, sizefactor):
        x1 = self.resolution[0] / ( 30 + 20 ) 
        x2 = self.resolution[1] / ( 34 ) 
        return min((x1, x2))

    def menu(self, name):
        show = True

        #pygame.display.toggle_fullscreen(): return bool
        #pygame.display.set_icon(Surface): return None

        m = Menu(self.menus[name])
        m.drawMenu()

        Clock = pygame.time.Clock()
        while show:
            tickFPS = Clock.tick(self.fps)

            for event in pygame.event.get():
                m.handleEvent(event)
                # quit the game if escape is pressed
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    m.activate()
                elif event.type == Menu.MENUCLICKEDEVENT:
                    if event.text == 'Quit':
                        return
                    elif event.item == 0:
                        isGameActive = True
                        m.deactivate()

            screen.blit(background, (0, 0))
            if m.isActive():
                m.drawMenu()
            else:
                background.fill((100, 0, 0))

            pygame.display.flip()

    def screen_transform(self, x, y):
        return (int(self.sizefactor*(y+1)), int(self.sizefactor*(x+1)))

    def gameloop(self):

        frame = 0
        mainloop = True
        init = False

        output('sdl.Play() starting with %s' % (self.resolution,), 'debug', source='Play().gameloop()')

        pygame.init()
        pygame.display.set_caption("%s | ESC for quit" % (self.caption))

        Clock = pygame.time.Clock()
        screen = pygame.display.set_mode(self.resolution)
        background = pygame.image.load('assets/bg_1024x768.jpg').convert()

        screen.blit(background, (0, 0))

        while mainloop:
            tickFPS = Clock.tick(self.fps)
            frame += 1

            if self.debug:
                pygame.display.set_caption("%s | ESC for quit | FPS: %.2f of %s" % (self.caption, Clock.get_fps(), self.fps))

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    mainloop = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mainloop = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    position = (int(round(event.pos[0] / self.sizefactor )), int(round(event.pos[1] / self.sizefactor )))
                    self.towers.append(Tower(event.pos[0], event.pos[1]))
                    self.commands.put({'res': 'send', 'path': 'towers', 'data': {'place': '%s,%s' % (position[0], position[1],)}})

            while not self.queue.empty():

                action = self.queue.get()
                #output('event to process: %s/' % action['res'], 'debug', source='Play().gameloop()] [QUEUE')

                if not init:
                    self.map.set_map(action['data'])
                    self.map.build_map()

                    for tileset in self.map.tiles:
                        self.rendered[tileset] = pygame.sprite.RenderPlain(self.map.tiles[tileset])

                    for tileset in self.rendered:
                        self.rendered[tileset].draw(screen)

                    init = True

                if action['res'] in ('send',):
                    self.commands.append(action['data'])

                elif action['res'] in ('walk',):
                    self.walk = action['data']

                elif action['res'] in ('enemies',):
                    self.enemies = []
                    for enemy in action['data']:
                        pos = enemy['pos']
                        digit = int(round(pos))

                        if len(self.walk) > ceil(pos):
                            x1, y1 = self.walk[int(floor(pos))]
                            x2, y2 = self.walk[int(ceil(pos))]
                            eps = pos - floor(pos)
                            x = x1 + (x2 - x1) * eps
                            y = y1 + (y2 - y1) * eps
                        else:
                            x, y = self.walk[-1]

                        self.enemies.append(Enemy(enemy['id'], enemy['hp'], 0, self.screen_transform(x, y), sizefactor=self.sizefactor))

                elif action['res'] in ('towers',):
                    pass

                    #for enemy in self.rendered['enemies']:
                        #self.rendered['enemies'].draw(screen)
                    #pass

                screen.blit(background, (0, 0))

                for tileset in self.rendered:
                    self.rendered[tileset].draw(screen)

                towers = pygame.sprite.RenderPlain(self.towers)
                towers.draw(screen)

                enemies = pygame.sprite.RenderPlain(self.enemies)
                enemies.draw(screen)

                self.rendered['spawn'].draw(screen)
                self.rendered['exit'].draw(screen)

                pygame.display.flip()

            pygame.display.update()

            if frame > (self.fps - 1):
                frame = 0

        pygame.quit()

        output('sdl.Play() exited', 'debug', source='Play().gameloop()')

def rect_from_picture(image, position=None):
    image_obj = pygame.image.load("assets/"+str(image))
    rect = image_obj.get_rect()
    if position is not None:
        rect[0] = position[0]
        rect[1] = position[1]

    return rect

def load_image(name, colorkey=None, scale=None):
    fullname = os.path.join('assets', name)

    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        output('Cannot load image: %s' % name, 'error')
        raise SystemExit, message

    if scale is not None:
        image = pygame.transform.scale(image, scale)

    image = image.convert()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()

def load_sound(name):
    fullname = os.path.join('assets', name)

    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer:
        return NoneSound()

    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        output('Cannot load sound: %s' % name, 'error')
        raise SystemExit, message

    return sound

