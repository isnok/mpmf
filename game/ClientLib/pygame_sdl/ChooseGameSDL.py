from twisted.python import log
from zope.interface import implements

from ClientLib.pygame_sdl.PygameBase import BaseSDLGame
from ClientLib.Interfaces import IWebWorld
from SharedLib.Interfaces import IGame

import pygame

class ChooseGameSDL(BaseSDLGame):

    implements(IGame)

    def startUp(self):
        self.games = {}
        pygame.display.set_caption("Choose a game! ESC or q to quit")
        self.screen = pygame.display.set_mode((1024,768))
        self.background = pygame.image.load('assets/bg_1024x768.jpg').convert()
        self.screen.blit(self.background, (0, 0))

        self.font = pygame.font.SysFont("monospace", 35)
        text = self.font.render("Choose a Game:", 1, (255,255,0), (0,0,255))
        self.screen.blit(text, (100, 100))

    def update(self, data):
        data = data['data']
        #log.msg("Update via %s" % data)
        self.clicks = []
        for cnt, game in enumerate(data):
            label = self.font.render(game, 1, (255,0,0), (0,255,0))
            pos = (100, 200 + 100 * cnt)
            self.screen.blit(label, pos)
            r = label.get_rect()
            r.topleft = pos
            self.clicks.append(r)
            self.games[pos] = game
        pygame.display.flip()
        pygame.display.update()

    def onClick(self, pos):
        clicked = [ r for r in self.clicks if r.collidepoint(pos) ]
        log.msg("CLICK! %s" % clicked)
        if clicked:
            game = self.games[clicked.pop().topleft]
            log.msg("CLACK! %s" % game)
            IWebWorld(333).update({'game': game})
