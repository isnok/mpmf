#!/usr/bin/env python
""" Game Server Launcher """

from zope.interface import implements
from SharedLib.Interfaces import IMainSetup

from argparse import ArgumentParser

class CmdlineSetup(ArgumentParser):
    implements(IMainSetup)

    def asDict(self, _=None):
        return vars(self.parse_args())

parser = CmdlineSetup(description="Defender Server")
parser.add_argument("-d", "--debug", default=False, action="store_true", help="debug foo")
parser.add_argument("-q", "--quiet", default=False, action="store_true", help="turn off statistics reporting")
parser.add_argument("-v", "--verbose", action='count', help="verbosity level")
parser.add_argument("-l", "--log", type=str, default="-", help="logfile ('-' for stdout)")
parser.add_argument("-p", "--port", type=int, default=3333, help="port to serve game(s) on")
parser.add_argument("-i", "--interface", type=str, default='', help="interface to serve game(s) on")
parser.add_argument("-P", "--passwordfile", type=str, default='server.passwd', help="password file to use")
args = parser.parse_args()

from SharedLib.component_hacks import registerGlobal
registerGlobal(args, IMainSetup)

import SharedLib.Logging
import ServeLib.Server

from ServeLib.Interfaces import IGameServer
server = IGameServer(parser)

from twisted.internet import reactor

if args.debug:

    def test():
        pass

    reactor.callLater(1, test)

reactor.run()
