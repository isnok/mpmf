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

class IdleClientAscii(BaseAsciiGame):

    implements(IGame)
    plays = "IdleGame"
    classProvides(IPlugin, IAsciiFrontend)

    def startUp(self):
        self.points = 0

    def handle(self):
        c = self.doMoves()
        y = IDrawingEngine(self).y
        if c == ord(' '):
            IWebWorld(self).update({'finish': self.name})

    def update(self, data):
        self.points = data['data']
        engine = IDrawingEngine(self)
        engine.screen.clear()
        engine.screen.addstr(5, 5, "Idle points: %s" % self.points)

        engine.screen.refresh()
        # move the cursor to the player
        curses.setsyx(engine.y, engine.x)
        curses.doupdate()
