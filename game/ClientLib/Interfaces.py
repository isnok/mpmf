from zope.interface import Interface
from zope.interface import Attribute
from twisted.application.service import IServiceCollection

class IClientSetup(Interface):
    host = Attribute("game host")
    port = Attribute("game port")
    game = Attribute("game name")
    user = Attribute("user name")

class IClient(Interface):
    """ The root process of a client. """

class IWebWorld(Interface):
    """ The headless representation of the game state. """

class IInputDeviceSupport(Interface):
    """ Mouse/Keyboard/-pad support """

class IDrawingEngine(Interface):
    """ A drawing engine for tiled worlds. """

class IClientPlugin(Interface):
    """ A plugin finder class for game front-/backends. """

class ISDLFrontend(IClientPlugin):
    """ A pygame frontend for a game. """

class IAsciiFrontend(IClientPlugin):
    """ A curses frontend for a game. """
