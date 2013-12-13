import pygame

from twisted.python import log
from twisted.internet import reactor

from zope.interface import implements
from ClientLib.Interfaces import IDrawingEngine
from SharedLib.Interfaces import IGame

from ClientLib.BaseRunner import BaseGameRunner


class SDLGameRunner(BaseGameRunner):

    implements(IDrawingEngine)

    def setUp(self):
        pygame.init()
        reactor.addSystemEventTrigger(
            'before', 'shutdown', pygame.quit)

from ClientLib.Interfaces import IClient
from twisted.python.components import registerAdapter
registerAdapter(SDLGameRunner, IClient, IDrawingEngine)
