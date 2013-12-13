from twisted.python import log
from twisted.internet import reactor
from ClientLib.BaseRunner import BaseGameRunner
from ClientLib.Interfaces import IDrawingEngine
from zope.interface import implements

import curses


class AsciiGameRunner(BaseGameRunner):

    implements(IDrawingEngine)

    def setUp(self):
        self.x = 40
        self.y = 12

        self.screen = curses.initscr()
        # dont echo keystrokes
        curses.noecho()
        # dont require pressing enter
        curses.cbreak()
        # handle special keys
        self.screen.keypad(1)

        begin_x = 23 ; begin_y = 7
        height = 5 ; width = 40
        self.window = curses.newwin(height, width, begin_y, begin_x)
        self.window.nodelay(1)

        reactor.addSystemEventTrigger(
            'before', 'shutdown', self.tearDown)

    def tearDown(self):

       # restore terminal
       self.screen.keypad(0)
       curses.nocbreak()
       curses.echo()
       curses.endwin()


from ClientLib.Interfaces import IClient
from twisted.python.components import registerAdapter
registerAdapter(AsciiGameRunner, IClient, IDrawingEngine)
