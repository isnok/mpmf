from twisted.python import log
from zope.interface import implements
from zope.interface import classProvides
from twisted.plugin import IPlugin
from SharedLib.Interfaces import IGame
from ServeLib.Interfaces import IServerPlugin
from ServeLib.Interfaces import IGameRoom
from ServeLib.ChooseGame import ChooseGame

from ServeLib.BaseGame import BaseGame
from twisted.internet.task import LoopingCall

class IdleGame(BaseGame):

    title = "IdleGame"

    implements(IGame)
    classProvides(IPlugin, IServerPlugin)

    def configure(self, config):
        self._loop = LoopingCall.withCount(self.update)
        self._interval = 1
        self.points = 0

    def startService(self):
        if not self.running:
            self._loop.start(self._interval)
        BaseGame.startService(self)

    def stopService(self):
        if self.running:
            self._loop.stop()
        BaseGame.stopService(self)

    def update(self, count):
        self.points += count * len(IGameRoom(self).players)

    def gotArgs(self, request):
        #self.log("IdleGame Args: %s" % request.args)
        if "finish" in request.args:
            finisher = request.args["finish"].pop()
            self.finish(finisher)

    def render_JSON(self, request):
        return self.points

    def render_HTML(self, request):
        room = IGameRoom(self)
        player = request.getSession()
        text = [ "I'm a game! <a href='/play/%s/json'>My json API.</a>" % (room.name)]
        text.append("You have collected %s idle points." % (self.points))
        text.append("<a href='/play/%s?finish=%s'>Finish me!</a>" % (room.name, player.name))
        return "<br>".join(text)

    def finish(self, finisher):
        self.log("%s finished by %s at %s points." % (self.title, finisher, self.points))
        for player in IGameRoom(self).players:
            points = self.points
            if player.name == finisher:
                points *= points
            else:
                points += 100
            self.log("%s gains %s points." % (player.name, points))
            player.score += points
        self.chainload(ChooseGame)
