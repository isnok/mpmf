from twisted.python import log
from zope.interface import implements
from SharedLib.Interfaces import IPlayer
from twisted.web.server import Session

from SharedLib.component_hacks import NamedComponentized

from ServeLib.Interfaces import IGameServer
from SharedLib.string_helpers import rndname

class Player(Session, NamedComponentized):

    """ Seen from the server side, a player is best represented as a session.
        Since players are registered at the gameserver via their names and
        everybody starts off as anonymous, players can change their name.
        That requires a little bit of extra logic keeping the refs up to date.
    """
    implements(IPlayer)
    sessionTimeout = 30

    def __init__(self, site, uid, **kw):
        Session.__init__(self, site, uid, **kw)
        self.in_room = None
        self.phonebook = IGameServer(-1).players
        name = 'anon-%s' % rndname(3,6)
        NamedComponentized.__init__(self, name)
        if not self.config.debug:
            self.sessionTimeout *= 60

    def configure(self, config):
        self.score = 0

    def getname(self):
        return self._name

    def setname(self, name):
        if name in self.phonebook:
            log.msg("Name taken: %s -> NoOp" % name)
            return
        if hasattr(self, '_name') and self._name is not None:
            self.leave()
            if self.config.debug:
                assert(self is self.phonebook.pop(self._name))
            else:
                del self.phonebook[self._name]
        self._name = name
        self.join()
        if self.config.debug:
            assert(self is self.phonebook.setdefault(name, self))
        else:
            self.phonebook[name] = self

    def delname(self):
        self.expire()

    name = property(getname, setname, delname)

    def expire(self):
        log.msg("Player idle: %s" % self.name)
        self.leave()
        self.phonebook.pop(self.name)
        Session.expire(self)

    def join(self, room=None):
        if not room:
            if not self.in_room:
                return
            room = self.in_room
        if self.in_room:
            if room is self.in_room:
                return
            self.leave()
        room.enter(self)
        self.in_room = room

    def leave(self, room=None):
        if not self.in_room:
            return
        if not room:
            room = self.in_room
        room.leave(self)
        self.in_room = None
