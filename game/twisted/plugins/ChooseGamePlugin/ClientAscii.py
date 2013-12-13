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

class ChooseGamePluginAscii(BaseAsciiGame):

    implements(IGame)
    plays = "ChooseGamePlugin"
    classProvides(IPlugin, IAsciiFrontend)

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
        data = data['data']
        self.games = data
        engine = IDrawingEngine(self)
        for cnt, game in enumerate(data):
            engine.screen.addstr(2+cnt, 5, game)

        engine.screen.refresh()
        # move the cursor to the player
        curses.setsyx(engine.y, engine.x)
        curses.doupdate()
