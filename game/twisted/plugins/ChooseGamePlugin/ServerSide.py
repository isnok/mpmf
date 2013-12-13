from zope.interface import implements
from ServeLib.Interfaces import IGameRoom
from SharedLib.Interfaces import IGame

from zope.interface import classProvides
from twisted.plugin import IPlugin
from ServeLib.Interfaces import IServerPlugin

from twisted.python import log
from ServeLib.Interfaces import IServerPlugin
from twisted.plugin import getPlugins
from SharedLib.string_helpers import ordinal
from ServeLib.BaseGame import BaseGame

from SharedLib.plugin_helpers import getServerGames

class ChooseGamePlugin(BaseGame):
    temporaryAdapter = False

    title = "ChooseGame, the Plugin"

    implements(IGame)
    classProvides(IPlugin, IServerPlugin)

    def configureSuper(self, room):
        self.name = "%s:choosplug" % (room.name,)

    def configure(self, config):
        self.games = getServerGames()
        self._data = dict(zip([x.__name__ for x in self.games], self.games))
        self.data = self._data.keys()
        self.log("plugins: %s" % len(self.games))

    def gotArgs(self, request):
        if "game" in request.args:
            choice = request.args['game'][0]
            self.validate(choice)

    def validate(self, name):
        if not name in self.data:
            self.log("Invalid choice: %s" % name)
            return
        self.log("Validated choice: %s" % name)
        self.chainload(self._data[name])

    def render_JSON(self, request):
        return self.data

    def render_HTML(self, request):
        room = IGameRoom(self)
        lines = ["Hiho! <a href=/play/%s/json>My Json.</a>" % room.name]
        lines.append("<br>For round %s you can choose from %s games:\n" % (self.original.round+1, len(self.games)))
        fmt = " * <a href=/play/%s?game=%s>%s option: %s</a>"
        for n, g in enumerate(self.games):
            lines.append(fmt % (room.name, g.__name__, ordinal(n+1), g.title))
        return "<br>".join(lines)
