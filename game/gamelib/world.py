from twisted.web.resource import Resource

from serverlib.jsonhttp import JsonResource
from serverlib.game import GameBackend

from pprint import pformat

class World(Resource):

    def __init__(self, host, name):
        self.host = host
        Resource.__init__(self)
        self.name = name
        self.game = GameBackend(self, name)
        self.players = ['dudeA', 'budeB', 'dudeB', 'Adude']

    def render_GET(self, request):
        html = "<html><body>Game: %r, Players: %s<br><pre>%s</pre></body></html>"
        stats = pformat(dict(self.game.stats.items()))
        return html % (self.name, len(self.players), stats)

    def getChild(self, name, request):
        if request.args:
            self.handleArgs(request.args)
        if name == '':
            return self
        elif name == 'players':
            return JsonResource(name, self.players)
        elif name == 'stop':
            return JsonResource(name, self.host.endGame(self.name))
        elif name == 'start':
            self.game.startService()
            return JsonResource(name, 'started')
        else:
            return self.game.getChild(name, request)

    def handleArgs(self, args):
        print "Received: %s" % args
        if 'join' in args:
            for player in args['join']:
                self.joined(player)
            return True
        if 'leave' in args:
            for player in args['leave']:
                self.leaved(player)
            return True
        if 'place' in args:
            try:
                tmp = args['place'].pop()
                x, y = map(int, tmp.split(","))
                return self.game.place_tower(x, y)
            except:
                return False
        if 'remove' in args:
            try:
                tmp = args['remove'].pop()
                x, y = map(int, tmp.split(","))
                return self.game.remove_tower(x, y)
            except:
                return False
        return False

    def joined(self, player):
        print "%s joinded the game." % player
        self.players.append(player)

    def leaved(self, player):
        try:
            self.players.remove(player)
            print "%s left the game." % player
        except:
            print "%s was not in the game. :-)" % player
