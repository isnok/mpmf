from twisted.python import log
from zope.interface import implements
from twisted.internet import reactor

from twisted.python.components import Adapter
from twisted.application.service import MultiService
from ServeLib.Interfaces import IRoomService

from SharedLib.component_hacks import registerIDs
from ServeLib.GameRoom import GameRoom
from ServeLib.Interfaces import IGameRoom
from ServeLib.Interfaces import IServerService

from zope.interface.verify import verifyObject


class ServerService(MultiService, Adapter):

    """ The Server MultiService.
    It interfaces some methods of a traditional dict,
    proxying them to the games dictionary of the GameServer.
    """

    implements(IServerService)

    def __init__(self, server):
        Adapter.__init__(self, server)
        MultiService.__init__(self)

        reactor.callWhenRunning(self.startService)
        reactor.addSystemEventTrigger("before", "shutdown", self.stopService)

        # from now on, new GameRooms can be created through
        # this adapter acting as the cache dict in registerIDs
        registerIDs(GameRoom, self, IRoomService)

        self.__getitem__   = self.namedServices.__getitem__
        self.__contains__  = self.namedServices.__contains__

    def addService(self, service):
        if hasattr(service, 'name') and service.name:
            assert(verifyObject(IRoomService, service))
        MultiService.addService(self, service)

    def __setitem__(self, name, room):
        assert(name == room.name)
        assert(verifyObject(IGameRoom, room))
        rooms = self.original.rooms[name] = room
        self.addService(IRoomService(room))

    def __delitem__(self, name):
        try:
            self.removeService(self.namedServices[name])
        except:
            pass
        try:
            del self.original.rooms[name]
        except:
            pass

    def setdefault(self, name, room):
        if name in self:
            return self[name]
        self[name] = room
        return room

from ServeLib.Interfaces import IGameServer
from twisted.python.components import registerAdapter
registerAdapter(ServerService, IGameServer, IServerService)
