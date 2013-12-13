from twisted.python import log
from zope.interface import implements
from ServeLib.Interfaces import IStatistics
from twisted.python.components import Adapter
from twisted.internet.task import LoopingCall
from pprint import pformat

class ServerStatistics(dict, Adapter):
    temporaryAdapter = True

    implements(IStatistics)

    def __init__(self, server):
        dict.__init__(self)
        Adapter.__init__(self, server)

    def __missing__(self, key):
        self[key] = 0
        return 0

from ServeLib.Interfaces import IGameServer
from twisted.python.components import registerAdapter
registerAdapter(ServerStatistics, IGameServer, IStatistics)

from ServeLib.Interfaces import IStatsProcessor
from ServeLib.Interfaces import IServerService
from ServeLib.Interfaces import IGameRoom
from twisted.application.service import Service
from SharedLib.string_helpers import ordinal

class StatsDaemon(Service, Adapter):

    implements(IStatsProcessor)
    interval = 10

    def __init__(self, server):
        Adapter.__init__(self, server)
        IServerService(self).addService(self)
        self._loop = LoopingCall(self.process)
        self.count = 0

    def collect(self):
        import gc
        gc.collect() # trigger weakref drops
        self.count += 1
        stats = IStatistics(self)
        onlineRooms = IGameServer(self).rooms
        roomStats = stats['rooms'] = {}
        roomStats['open'] = len(onlineRooms)
        def countPlayers(name):
            room = IGameRoom(name)
            return "%s (%s)" % (name, len(room.players))
        roomStats['names'] = map(countPlayers, onlineRooms.keys())
        onlinePlayers = IGameServer(self).players
        playerStats = stats['players'] = {}
        playerStats['online'] = len(onlinePlayers)
        playerStats['ladder'] = sorted([(p.score, p.name) for p in onlinePlayers.values()])
        # sum([len(r.players) for r in onlineRooms.values()])
        return stats

    def report(self, stats):
        fmt = "=== %s Server Statistics Report ===\n%s"
        log.msg(fmt % (ordinal(self.count), pformat(stats)))

    def process(self):
        self.report(self.collect())

    def startService(self):
        if not self.running:
            self._loop.start(self.interval)
        Service.startService(self)

    def stopService(self):
        if self.running:
            self._loop.stop()
        Service.stopService(self)

registerAdapter(StatsDaemon, IGameServer, IStatsProcessor)
