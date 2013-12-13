from twisted.python import log
from zope.interface import implements

from twisted.python.components import Componentized
from ServeLib.Interfaces import IGameServer
from SharedLib.component_hacks import registerGlobal
from SharedLib.component_hacks import registerIDs

from twisted.internet import reactor
from ServeLib.Interfaces import IServerService
from ServeLib.Interfaces import IServerSite
from ServeLib.Interfaces import IGameRoom
from SharedLib.Interfaces import IPlayer
from ServeLib.GameRoom import GameRoom

from weakref import WeakValueDictionary

import ServeLib.ServerSite
import ServeLib.ServerService

class GameServer(Componentized):

    implements(IGameServer)

    def __init__(self, setup):
        Componentized.__init__(self)
        self.config = setup.asDict()

        # anyone adapting an IGameServer from a str/int/None will get me
        registerGlobal(self, IGameServer)

        self.rooms = WeakValueDictionary()
        self.players = WeakValueDictionary()

        registerIDs(GameRoom, self.rooms, IGameRoom)
        registerIDs(lambda: explode(), self.players, IPlayer)

        # init required components
        IServerService(self)
        IServerSite(self)

        if not self.config['quiet']:
            from ServeLib.Interfaces import IStatsProcessor
            import ServeLib.Statistics
            IStatsProcessor(self)

from twisted.python.components import registerAdapter
from SharedLib.Interfaces import IMainSetup
registerAdapter(GameServer, IMainSetup, IGameServer)
