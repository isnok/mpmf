#from zope.interface import implements
from twisted.python.components import Adapter
from twisted.application.service import Service
from SharedLib.Interfaces import IGame
from SharedLib.component_hacks import NamedAdapter

from twisted.python import log

class BaseGame(Service, NamedAdapter):

    def __init__(self, room):
        self.configureSuper(room)
        NamedAdapter.__init__(self, room)

    def configureSuper(self, room):
        room.round += 1
        self.name = "%s:round%s" % (room.name, room.round)

    def startService(self):
        self.log("start")
        Service.startService(self)

    def stopService(self):
        self.log("ended")
        return Service.stopService(self)

    def gotArgs(self, request):
        log.msg("Got Args: %s" % request.args)

    def render_HTML(self, request):
        return "Emptyness."

    def render_JSON(self, request):
        return None

    def chainload(self, game):
        room = self.original
        room.setAdapter(IGame, game)
        IGame(room).startService()
        self.stopService()
