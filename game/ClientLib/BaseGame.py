
from twisted.python import log
from SharedLib.component_hacks import NamedAdapter

class ClientBaseGame(NamedAdapter):

    def __init__(self, client):
        NamedAdapter.__init__(self, client)
        self.startUp()

    def startUp(self):
        """ a replacement for __init__ """

    def handle(self):
        raise NotImplementedError()

    def update(self, data):
        raise NotImplementedError()
