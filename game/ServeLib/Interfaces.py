from zope.interface import Interface
from zope.interface import Attribute

from twisted.application.service import IService
from twisted.application.service import IServiceCollection
from twisted.plugin import IPlugin

class IGameServer(Interface):
    """ The game server's root struct. """
    games = Attribute("dict: names -> game rooms")
    def newGame(self, name):
        """ creates a new game room """

class IServerService(IServiceCollection):
    """ The Service of the room host. """

class IStatistics(Interface):
    """ Numbers moving. """

class IStatsProcessor(IService):
    """ periodically process stats """

class IGameRoom(Interface):
    """ Here the players meet and up to one round can be played at a time. """
    players = Attribute("players in room")
    #game = Attribute("the current game")

class IRoomService(IService):
    """ The Service of an open room. """

class IServerSite(Interface):
    """ The Servers Site deals with authentication and users. """

class IServerPlugin(Interface):
    """ An interface to find games via the plugin mechanism. """
    title = Attribute("name of the game")
