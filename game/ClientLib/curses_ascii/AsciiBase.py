import pygame

from twisted.python import log
from twisted.internet import reactor

from ClientLib.BaseGame import ClientBaseGame
from ClientLib.Interfaces import IDrawingEngine


class BaseAsciiGame(ClientBaseGame):

    def startUp(self):
        raise NotImplementedError()

    def handle(self):
        self.doMoves()

    def doMoves(self):
        engine = IDrawingEngine(self)
        c = engine.window.getch()
        if   c == ord('q'): reactor.stop()
        elif c == ord('h'): engine.x -= 1
        elif c == ord('j'): engine.y += 1
        elif c == ord('k'): engine.y -= 1
        elif c == ord('l'): engine.x += 1
        elif c == ord('y'):
                engine.y -= 1
                engine.x -= 1
        elif c == ord('u'):
                engine.y -= 1
                engine.x += 1
        elif c == ord('b'):
                engine.y += 1
                engine.x -= 1
        elif c == ord('n'):
                engine.y += 1
                engine.x += 1
        return c

    def update(self, data):
        raise NotImplementedError()
