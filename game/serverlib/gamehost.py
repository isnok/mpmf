from twisted.python import log
from twisted.web.resource import Resource

import json

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.application.service import MultiService
from gamelib.world import World

from twisted.internet.task import LoopingCall

class GameHostResource(Resource, MultiService):

    def __init__(self, args):
        Resource.__init__(self)
        MultiService.__init__(self)
        self.port = args.port
        self.interface = args.interface
        self.games = {}
        self.statsreport = LoopingCall(self.report)

    def startService(self):
        log.msg("Listening on %s:%s" % (self.interface, self.port))
        reactor.addSystemEventTrigger(
            "before", "shutdown", self.stopService
        )

        factory = Site(self)
        factory.log = lambda request: None

        reactor.listenTCP(
            self.port,
            factory,
            interface=self.interface
        )
        self.statsreport.start(5.0)
        MultiService.startService(self)

    def delChild(self, name, child):
        child.server = None
        del self.children[name]

    def newGame(self, name, request):
        new = World(self, name)
        self.putChild(name, new)
        new.game.setServiceParent(self)
        return self.games.setdefault(name, new)

    def endGame(self, name, request=None):
        if not name in self.games:
            error = "Game to end (%r) did not exist." % name
            log.err(error)
            return error
        old = self.games.pop(name)
        old.game.stopService()
        old.game.disownServiceParent()
        self.delChild(name, old)
        log.msg("Game %r ended." % name)

    def getChild(self, name, request):
        if name == '':
            return self
        elif name == 'stop':
            return StopServe()
        elif name in self.games:
            return self.games[name]
        else:
            return self.newGame(name, request)

    def render_GET(self, request):
        return "There are currently %d games ongoing.<br>%s" % (
                len(self.games),
                '<br>'.join(self.games.keys())
            )

    def report(self):
        log.msg("=== Server stats (%s games) ===" % len(self.games))
        for name, game in self.games.iteritems():
            log.msg("Game %r: %s" % (name, dict(game.game.stats)))


class StopServe(Resource):

    def render_GET(self, request):
        reactor.stop()

class AliveServe(Resource):

    def render_GET(self, request):
        return self.build_response(None)
