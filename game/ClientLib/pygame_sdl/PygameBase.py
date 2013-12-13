import pygame

from twisted.python import log
from twisted.internet import reactor

from ClientLib.BaseGame import ClientBaseGame

class BaseSDLGame(ClientBaseGame):

    def startUp(self):
        raise NotImplementedError()

    def handle(self):
        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONUP:
                self.onClick(pygame.mouse.get_pos())
                continue

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_q] or pressed[pygame.K_ESCAPE]:
                reactor.stop()

    def onClick(self, pos):
        raise NotImplementedError()

    def update(self, data):
        raise NotImplementedError()
