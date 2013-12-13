from twisted.python import log
from zope.interface import implements

from twisted.python.components import Adapter
from twisted.web.resource import IResource
from twisted.web.resource import Resource
from SharedLib.Interfaces import IMainSetup
from ServeLib.Interfaces import IGameRoom
from SharedLib.Interfaces import IGame
from SharedLib.string_helpers import rndname

from twisted.web.guard import HTTPAuthSessionWrapper
from twisted.web.guard import DigestCredentialFactory
#from twisted.web.guard import BasicCredentialFactory
#from twisted.cred.checkers import ANONYMOUS
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import Portal

#from hashlib import sha256

#from twisted.cred.checkers import AllowAnonymousAccess
#from twisted.cred.credentials import IAnonymous

class LogoutResource:
    implements(IResource)
    def render(self, request):
        request.getSession().expire()
        return "Logged out. <a href='/'>Go back.</a>"

class ServerResource(Resource, Adapter):

    implements(IResource)

    def __init__(self, server):
        Adapter.__init__(self, server)
        Resource.__init__(self)

        portal = Portal(LoginRealm())
        # todo: get this to work (to not store user passwords in plaintext)
        #passwordDB = FilePasswordDB('server.passwd', hash=lambda p: sha256(p).hexdigest())
        args = IMainSetup(100)
        passwordDB = FilePasswordDB(args.passwordfile)
        portal.registerChecker(passwordDB)
        # does not work as i expected: (keeping it still for the memories :)
        #portal.registerChecker(AllowAnonymousAccess(), IAnonymous)

        wrapper = HTTPAuthSessionWrapper(portal, [DigestCredentialFactory('md5', 'game_server')])
        #wrapper = HTTPAuthSessionWrapper(portal, [BasicCredentialFactory('game_server')])

        self.loginWrapper = wrapper
        self.putChild("login", wrapper)
        self.putChild("logout", LogoutResource())

    def getChild(self, name, request):
        player = request.getSession()
        if name == 'play' and request.postpath and request.postpath[0]:
            game = IGameRoom(request.postpath[0])
            request.getSession().join(game)
            return IResource(game)
        elif name == 'register' and set(['name', 'password']).issubset(request.args):
            name = request.args['name'].pop()
            password = request.args['password'].pop()
            return RegisterResource(name, password)
        return self

    def render(self, request):
        def link(tup):
            name, room = tup
            title = IGame(room).title
            names = [p.name for p in room.players]
            return '<a href="/play/%s">%s: %s</a> - %d player(s): %s' % (name, name, title, len(names), ", ".join(names))
        games = "<br>".join(map(link, IGameServer(self).rooms.items()))
        player = request.getSession()
        text = [ "Hello %s!" % player.name ]
        text.append('I\'m a game server. <a href="login">Log in</a> or <a href="logout">out</a> to change your name.')
        text.append('Games in progress:<pre>%s</pre>' % games)
        text.append('<a href="/play/%s">Create a random game.</a>' % rndname())
        return "<br>".join(text)

from twisted.python.components import registerAdapter
from ServeLib.Interfaces import IGameServer
registerAdapter(ServerResource, IGameServer, IResource)


from twisted.internet import reactor
from twisted.cred.portal import IRealm

class LoginRealm(object):

    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if avatarId == "halt":
            log.msg("Authorized halt request: %s %s %s" % (avatarId, mind, interfaces))
            reactor.stop()
        if IResource in interfaces:
            return IResource, LoginResource(avatarId), lambda: None
        raise NotImplementedError()


from twisted.web.resource import Resource

class LoginResource(Resource):
    isLeaf = True

    def __init__(self, name):
        Resource.__init__(self)
        self.name = name

    def render(self, request):
        session = request.getSession()
        log.msg("Authorized: %s" % session.name)
        session.name = self.name
        return 'Authorized! %s<br><a href="/">Back to main.</a>' % session.name


import string
ok_chars = string.letters + string.digits
def sanitize(in_string):
    return filter(lambda c: c in ok_chars, in_string)

class RegisterResource(Resource):
    isLeaf = True

    def __init__(self, name, password):
        Resource.__init__(self)
        self.name = sanitize(name)
        self.password = sanitize(password)

    def render(self, request):
        if not self.name:
            return "Invalid name: %s" % self.name
        elif not self.password:
            return "Your password consists only of 'bad' characters."
        session = request.getSession()
        passfile = IMainSetup(100).passwordfile
        passDB = FilePasswordDB(passfile)
        try:
            passDB.getUser(self.name)
            log.msg("Already taken: %s" % self.name)
            return "Sorry, the name %r is already taken." % self.name
        except KeyError:
            session.name = self.name
            with open(passfile, 'a') as f:
                f.write("%s:%s\n" % (self.name, self.password))
            log.msg("Registered: %s:%s" % (self.name, self.password))
            return 'Registered! %s - %s<br><a href="/">Back to main.</a>' % (session.name, self.password)
