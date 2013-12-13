from twisted.python import log
from zope.interface import implements
from ClientLib.Interfaces import IClient
from ClientLib.Interfaces import IWebWorld
from SharedLib.component_hacks import registerGlobal

from twisted.internet import reactor
from twisted.application.service import MultiService
from SharedLib.component_hacks import NamedComponentized

from twisted.web.client import HTTPClientFactory

import ClientLib.Fetcher

class ClientBase(MultiService, NamedComponentized):

    implements(IClient)

    def __init__(self, parser):
        MultiService.__init__(self)
        NamedComponentized.__init__(self, parser.parse_args().game)
        if not self.config.verbose:
            HTTPClientFactory.noisy = False
        registerGlobal(self, IClient)
        self.addService(IWebWorld(self))

    def start(self):
        self.startService()
        reactor.run()

from twisted.python.components import registerAdapter
from SharedLib.Interfaces import IMainSetup
registerAdapter(ClientBase, IMainSetup, IClient)

if IMainSetup(99).ascii:
    import ClientLib.curses_ascii.AsciiClient
else:
    import ClientLib.pygame_sdl.SDLClient
