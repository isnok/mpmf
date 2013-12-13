from zope.interface import Interface
from zope.interface import Attribute

#from twisted.application.service import IService
#from twisted.application.service import IServiceCollection
#from twisted.plugin import IPlugin

class IMainSetup(Interface):
    """ Setup of the launched application (commanline args by now). """
    def asDict(self):
        """ return a dict of the config """

class IGame(Interface):
    """ A game that can be played by one or more players. """

class IPlayer(Interface):
    """ Player Session """
    name = Attribute("name of the player")
