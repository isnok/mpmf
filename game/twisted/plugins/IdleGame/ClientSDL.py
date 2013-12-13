import pygame
from pygame.locals import *

from twisted.python import log
from ClientLib.pygame_sdl.PygameBase import BaseSDLGame
from ClientLib.Interfaces import IWebWorld

#from zope.interface import implements
from zope.interface import classProvides
from twisted.plugin import IPlugin
#from ClientLib.Interfaces import IClientPlugin
from ClientLib.Interfaces import ISDLFrontend

class IdleClientSDL(BaseSDLGame):

    plays = 'IdleGame'
    classProvides(IPlugin, ISDLFrontend)

    def startUp(self):
        self.games = {}
        pygame.display.set_caption("Play IdleGame! ESC or q to quit")
        self.screen = pygame.display.set_mode((1024,768))
        self.background = pygame.image.load('assets/starfield_background-1024x770.jpg').convert()
        self.screen.blit(self.background, (0, 0))

        self.font = pygame.font.SysFont("monospace", 35)
        text = self.font.render("IdleGame!", 1, (255,255,0), (0,0,255))
        self.screen.blit(text, (100, 100))

    def update(self, data):
        data = data['data']
        label = self.font.render("IdleScore: %s" % (data,), 1, (255,0,0), (0,255,0))
        pos = (100, 200)
        self.screen.blit(label, pos)
        pygame.display.flip()
        pygame.display.update()

    def onClick(self, pos):
        log.msg("You stopped idling!")
        IWebWorld(333).update({'finish': 'lolo'})
