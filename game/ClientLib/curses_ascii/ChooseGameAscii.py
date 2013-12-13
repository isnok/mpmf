from twisted.python import log
from zope.interface import implements

from ClientLib.curses_ascii.AsciiBase import BaseAsciiGame
from ClientLib.Interfaces import IWebWorld
from ClientLib.Interfaces import IDrawingEngine
from SharedLib.Interfaces import IGame

import curses

class ChooseGameAscii(BaseAsciiGame):

    implements(IGame)

    def startUp(self):
        self.games = []

    def handle(self):
        c = self.doMoves()
        y = IDrawingEngine(self).y
        if c == ord(' ') and y - 2 < len(self.games):
            IWebWorld(self).update({'game': self.games[y-2]})
        #elif c == ord('X'): self.world.destroy()
        #elif c == ord(' '): self.world.place_tower(self.y, player.x)


    def update(self, data):
        self.games = data['data']
        engine = IDrawingEngine(self)
        engine.screen.clear()
        engine.screen.addstr(0, 3, "name: %(you)s - score: %(your_score)s" % data)
        for cnt, game in enumerate(self.games):
            engine.screen.addstr(2+cnt, 5, game)

        engine.screen.refresh()
        # move the cursor to the player
        curses.setsyx(engine.y, engine.x)
        curses.doupdate()
