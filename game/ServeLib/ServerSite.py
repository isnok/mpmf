from twisted.python import log
from twisted.internet import reactor
from zope.interface import implements
from twisted.python.components import Adapter
from twisted.python.components import registerAdapter

from twisted.web.server import Site
from ServeLib.Interfaces import IServerSite
from SharedLib.Interfaces import IMainSetup
from ServeLib.Interfaces import IGameServer
from twisted.web.resource import IResource

from ServeLib.Player import Player
from SharedLib.component_hacks import registerIDs

import ServeLib.ServerResource


class ServerSite(Site, Adapter):

    implements(IServerSite)

    sessionFactory = Player

    def __init__(self, server):
        Adapter.__init__(self, server)
        Site.__init__(self, IResource(self))
        reactor.callWhenRunning(self.startListening)

    def startListening(self):
        args = IMainSetup(42)
        if not args.verbose:
            self.log = lambda request: None
        log.msg("listening on %s:%s" % (args.interface, args.port))
        reactor.listenTCP(args.port, self, interface=args.interface)

    def makeSession(self):
        player = Site.makeSession(self)
        return player

registerAdapter(ServerSite, IGameServer, IServerSite)
