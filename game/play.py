#!/usr/bin/env python

import random

from zope.interface import implements
from SharedLib.Interfaces import IMainSetup

from argparse import ArgumentParser

class CmdlineSetup(ArgumentParser):
    implements(IMainSetup)

    def asDict(self, _=None):
        return vars(self.parse_args())

parser = CmdlineSetup(description="Defender Client Launcher")
parser.add_argument(
    "-a", "--ascii", action='store_true', default=False,
    help="use curses client (default: pygame)")
parser.add_argument(
    "-F", "--fullscreen", action='store_true', default=False,
    help="fullscreen mode (pygame only)")
parser.add_argument(
    "-u", "--username", default='anon-user',
    help="username")
parser.add_argument(
    "-p", "--password", default=None,
    help="password")
parser.add_argument(
    "-H", "--host", default='localhost',
    help="server host")
parser.add_argument(
    "-P", "--port", default='3333',
    help="server port")
parser.add_argument(
    "-g", "--game", default='sdlplay',
    help="game name")
parser.add_argument(
    "-l", "--log", default='-',
    help="logfile (ascii version only)")
parser.add_argument(
    "-d", "--debug", action="store_true",
    help="debug mode")
parser.add_argument(
    "-q", "--quiet", default=False, action="store_true",
    help="turn off statistics reporting")
parser.add_argument(
    "-v", "--verbose", action="store_true", default=False,
    help="be verbose")

args = parser.parse_args()

from SharedLib.component_hacks import registerGlobal
registerGlobal(args, IMainSetup)

from SharedLib import Logging

import ClientLib.Client

from ClientLib.Interfaces import IClient

IClient(parser).start()
