from ClientLib.curses_ascii.AsciiBase import BaseAsciiGame
from ClientLib.Interfaces import IWebWorld
from ClientLib.Interfaces import IDrawingEngine
from SharedLib.Interfaces import IGame

import curses

from zope.interface import implements
from zope.interface import classProvides
from twisted.plugin import IPlugin
#from ClientLib.Interfaces import IClientPlugin
from ClientLib.Interfaces import IAsciiFrontend

from math import ceil, floor

class SimpleTDClientAscii(BaseAsciiGame):

    implements(IGame)
    plays = 'SimpleTD'
    classProvides(IPlugin, IAsciiFrontend)

    def startUp(self):
        self.world = None
        IWebWorld(self).update({'static': 'true'})

    def handle(self):
        c = self.doMoves()
        if c == ord(' '):
            engine = IDrawingEngine(self)
            coords = "%s,%s" % (engine.y, engine.x)
            IWebWorld(self).update({'place': coords})
        #elif c == ord('X'): self.world.destroy()
        #elif c == ord(' '): self.world.place_tower(self.y, player.x)


    def init_map(self, mapdata):
        self.world = []
        for y, row in enumerate(mapdata):
            line = ''
            for x, desc in enumerate(row):
                line += {
                    'free'   : ' ',
                    'walk'   : ':',
                    'spawn'  : '$',
                    'exit'   : '*',
                    'blocked': '#',
                }[desc]
            self.world.append(line)

    def update(self, data):
        data = data['data']
        if 'map' in data:
            self.init_map(data['map'])
            self.walk = data['walk']
        if not self.world:
            return
        engine = IDrawingEngine(self)
        engine.screen.clear()
        for cnt, line in enumerate(self.world):
            engine.screen.addstr(cnt, 0, line)

        for tow in data['towers']:
            y, x = tow['x'], tow['y']
            engine.screen.addstr(y, x, 'O')

        for ene in data['enemies']:
            x, y = self.pos_to_coord(ene['pos'], self.walk)
            engine.screen.addstr(y, x, 'X')

        engine.screen.refresh()
        # move the cursor to the player
        curses.setsyx(engine.y, engine.x)
        curses.doupdate()

    def pos_to_coord(self, pos, walk):
        if len(walk) > ceil(pos):
            x1, y1 = walk[int(floor(pos))]
            x2, y2 = walk[int(ceil(pos))]
            eps = pos - floor(pos)
            x = x1 + (x2 - x1) * eps
            y = y1 + (y2 - y1) * eps
        else:
            x, y = walk[-1]
        return int(round(y)), int(round(x))
