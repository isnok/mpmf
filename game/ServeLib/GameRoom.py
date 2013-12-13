from twisted.python import log
from ServeLib.Interfaces import IGameRoom
from ServeLib.Interfaces import IServerService
from SharedLib.component_hacks import NamedComponentized
from ServeLib.Interfaces import IGameServer
from zope.interface import implements
from twisted.internet import reactor

class GameRoom(NamedComponentized):

    implements(IGameRoom)

    def configure(self, config):
        self.players = []
        self.round = 0
        self.emptyTimeout = config.debug and 5 or 300
        self._closeCall = None

    def enter(self, player):
        log.msg("%s enters %s." % (player.name, self.name))
        if self._closeCall:
            self._closeCall.cancel()
            self._closeCall = None
        self.players.append(player)

    def leave(self, player):
        log.msg("%s leaves %s." % (player.name, self.name))
        self.players.remove(player)
        if self._closeCall is None and not self.players:
            if not self.emptyTimeout:
                self.closeIfEmpty()
            else:
                log.msg("schedule %ss: close(%s)" % (self.emptyTimeout, self.name))
                self._closeCall = reactor.callLater(self.emptyTimeout, self.closeIfEmpty)

    def closeIfEmpty(self):
        if not self.players:
            log.msg("close: %s" % self.name)
            service = IServerService(IGameServer(23))
            del service[self.name]

from twisted.python.components import Adapter
from twisted.application.service import Service
from SharedLib.Interfaces import IGame
from ServeLib.Interfaces import IRoomService
import ServeLib.ChooseGame

class RoomService(Service, Adapter):

    implements(IRoomService)

    def __init__(self, room):
        Adapter.__init__(self, room)
        self.name = room.name

    def startService(self):
        log.msg("Room open: %s" % self.name)
        IGame(self).startService()
        Service.startService(self)

    def stopService(self):
        log.msg("Room close: %s" % self.name)
        IGame(self).stopService()
        return Service.stopService(self)

from twisted.python.components import registerAdapter
registerAdapter(RoomService, IGameRoom, IRoomService)


from twisted.web.resource import IResource
from twisted.web.resource import Resource

import json

from SharedLib.component_hacks import NamedAdapter

class RoomResource(Resource, NamedAdapter):

    implements(IResource)

    def __init__(self, server):
        NamedAdapter.__init__(self, server)
        Resource.__init__(self)

    def getChild(self, name, request):
        # if any path element is json, set a flag
        if name == 'json':
            request.wantsJSON = True
        return self

    def gotArgs(self, request):
        """ Here we handle arguments to the game room. """

    def render(self, request):
        if request.args:
            self.gotArgs(request)
            IGame(self).gotArgs(request)

        if hasattr(request, 'wantsJSON'):
            return self.render_JSON(request)
        else:
            return self.render_HTML(request)

    def render_JSON(self, request):
        request.setHeader("content-type", "application/json")
        game = IGame(self)
        player = request.getSession()
        return json.dumps({
            'room': self.name,
            'game': game.__class__.__name__,
            'data': game.render_JSON(request),
            'you': player.name,
            'your_score': player.score,
        })

    def render_HTML(self, request):
        if request.args:
            head = '<head><meta http-equiv="refresh" content="1; url=/play/%s" ></head>' % self.name
        else:
            head = '<head><meta http-equiv="refresh" content="1" ></head>'

        game = IGame(self)
        room = IGameRoom(self)
        player = request.getSession()
        text = [ "Hello %s, welcome to %s." % (player.name, self.name) ]
        text.append('You can <a href="/">go back</a> or play a game.<br>')
        text.append('You have %s points.' % player.score)
        text.append('People in this room: %s' % [p.name for p in room.players])
        text.append("This game is called %r." % game.title)
        text.append("Try it yourself, it's fun!")
        text.append('')
        text.append("<pre>%s</pre>" % game.render_HTML(request))

        body = "<body>%s</body>" % "<br>".join(text)
        return "<html>%s%s</html>" % (head, body)

registerAdapter(RoomResource, IGameRoom, IResource)
