from twisted.python import log
from twisted.internet import reactor

from zope.interface import implements
from twisted.python.components import Adapter
from ClientLib.Interfaces import IDrawingEngine
from SharedLib.Interfaces import IGame
from SharedLib.plugin_helpers import getClientGames
from SharedLib.component_hacks import NamedAdapter


class BaseGameRunner(NamedAdapter):

    implements(IDrawingEngine)

    def configure(self, config):

        self.setUp()

        self.games = getClientGames()
        self.log('Game backends: %s' % self.games.keys())

        self.ongoing = None

    def setUp(self):
        raise NotImplementedError()

    def switchGame(self, name):
        self.log('Switching game from %s to %s.' % (self.ongoing, name))
        #try:
        game = self.games[name](self.original)
        self.original.setComponent(IGame, game)
        #except:
            #reactor.stop()
            #raise RuntimeError("Could not start game: %s" % name)
        self.ongoing = name

    def update(self, data):
        name = data['game']
        if not name == self.ongoing:
            self.switchGame(name)
        game = IGame(self)
        game.update(data)
        game.handle()
