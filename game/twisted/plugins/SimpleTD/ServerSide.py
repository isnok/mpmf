from twisted.python import log
from zope.interface import implements
from zope.interface import classProvides
from twisted.plugin import IPlugin
from SharedLib.Interfaces import IGame
from ServeLib.Interfaces import IServerPlugin
from ServeLib.Interfaces import IGameRoom
from ServeLib.ChooseGame import ChooseGame

from ServeLib.BaseGame import BaseGame
from twisted.internet.task import LoopingCall

from random import randint
from mapgen import gen_map

from random import random as rnd
from random import randint

from twisted.internet import reactor

class Tower:

    def __init__(self, game, x, y, owner):
        self.game = game
        self.owner = owner
        self.x = x
        self.y = y
        self.area = set()
        for dx in range(-3,4):
            for dy in range(-3,4):
                self.area.add((self.x+dx, self.y+dy))
        self.shoot = None
        self.cooldown = False

    def to_json(self):
        return {
            'x': self.x,
            'y': self.y,
            'owner': self.owner.name,
            #'shoots': sorted(self.area)}
        }

    def update(self, delta):

        if self.cooldown:
            return

        walk = self.game.walk
        if self.shoot is None and walk:
            #log.msg("shoot setup (%s,%s)" % (self.x, self.y))
            self.shoot = set((walk.index(c) for c in self.area.intersection(walk)))
            #log.msg("tower will shoot: %s" % self.shoot)

        bam = self.shoot.intersection(map(self.enemy_coord_idx, self.game.enemies))
        if bam:
            prey = max(bam)
            hits = filter(lambda e: self.enemy_coord_idx(e) == prey, self.game.enemies)
            msg = []
            for enemy in hits:
                dmg = randint(1,2)
                enemy.hp -= dmg
                if enemy.hp <= 0:
                    self.owner.score += dmg * 10
                    #log.msg("%s gains %d points." % (self.owner, dmg * 10))
                msg.append((enemy.id, enemy.at, dmg))
            #log.msg("(%s,%s) dmg stats: %s" % (self.x, self.y, msg))
            self.cooldown = True
            reactor.callLater(0.7, self.unfreeze)

    def unfreeze(self):
        self.cooldown = False

    def enemy_coord_idx(self, enemy):
        return int(round(enemy.at))

class Enemy:

    def __init__(self, towalk, level=1):
        self.level = level
        self.towalk = towalk
        self.speed = 4.5
        self.hp = 3**level
        self.at = 0
        self.id = "e:%05x" % randint(0, 1<<20)

    def to_json(self):
        return {'id': self.id, 'hp': self.hp, 'pos': self.at}

    def update(self, delta):
        if self.hp <= 0:
            return  "died"
        if self.at > self.towalk:
            #print "Whahaha! I got through! (hp:%s)" % (self.hp)
            return  "escaped"
        else:
            self.at += self.speed * delta + 0.1 * rnd()


from pprint import pformat
from collections import defaultdict

class SimpleTD(BaseGame):

    title = "Simple Tower Defense"

    implements(IGame)
    classProvides(IPlugin, IServerPlugin)

    def configure(self, config):
        room = self.original
        self._loop = LoopingCall.withCount(self.update)
        self._interval = 0.1
        self.map, self.walk = gen_map()
        self.tick = 0
        self.enemies = []
        self.towers = []
        self.spawned = 0
        self.stats = defaultdict(int)

    def startService(self):
        if not self.running:
            self._loop.start(self._interval)
        BaseGame.startService(self)

    def stopService(self):
        if self.running:
            self._loop.stop()
        BaseGame.stopService(self)

    def update(self, count):
        if not self.running:
            return

        if not (self.tick % 100):
            self.log("%(spawned)s/%(died)s/%(escaped)s enemies spawned/killed/escaped." % self.stats)

        self.tick += 1
        if self.stats['spawned'] < 100 and not randint(0,3):
            self.spawn("painin sias")
        elif self.stats['spawned'] >= 100 and not self.enemies:
            self.finish('towerforce')

        for t in self.towers:
            t.update(self._interval * count)

        dead = []
        for enemy in self.enemies:
            died = enemy.update(self._interval * count)
            if died:
                dead.append((died, enemy))

        for (reason, d) in dead:
            try:
                self.enemies.remove(d)
                #self.log("%s: %s" % (reason, d.to_json()))
                self.stats[reason] += 1
            except:
                pass

    def genData(self, static=False):

        data = {
            'time': self.tick,
            'enemies': [e.to_json() for e in self.enemies],
            'towers': [t.to_json() for t in self.towers],
        }

        if static:
            data.update({
                'map': self.map,
                'walk': self.walk,
            })

        return data

    def gotArgs(self, request):
        #self.log("IdleGame Args: %s" % request.args)
        if "place" in request.args:
            try:
                x, y = request.args['place'][0].split(',')
            except:
                return
            self.place_tower(int(x), int(y), request.getSession())
        if 'finish' in request.args:
            finisher = request.getSession().name
            self.finish(finisher)

    def render_JSON(self, request):
        static = 'static' in request.args
        return self.genData(static)

    def render_HTML(self, request):
        room = IGameRoom(self)
        player = request.getSession()
        text = [ "I'm a tower defense game! <a href='/play/%s/json'>My json API.</a>" % (room.name)]
        text.append("My data:\n%s" % pformat(self.genData()))
        text.append("<a href='/play/%s?finish=%s'>Finish me!</a>" % (room.name, player.name))
        return "<br>".join(text)

    def finish(self, finisher=None):
        if finisher:
            resumee = pformat(dict(self.stats))
            self.log("%s ended the game:\n%s" % (finisher, resumee))
        self.chainload(ChooseGame)

    def place_tower(self, x, y, placer=None):
        if self.remove_tower(x, y, placer):
            return True
        if self.map[x][y] == 'free':
            self.towers.append(Tower(self, x, y, placer))
            self.log("%s built at (%s,%s)." % (placer.name, x,y))
            self.stats['towers'] += 1
            self.stats['towers_built'] += 1
            return True
        else:
            self.log("Tower deny at (%s,%s)." % (x,y))
            return False

    def remove_tower(self, x, y, remover=None):
        towers = filter(lambda t: t.x == x and t.y == y, self.towers)
        if not towers:
            return False
        tower = towers.pop()
        if not remover == tower.owner:
            self.log("Steal? %s < %s" % (remover, tower.owner))
            self.stats['towers_stolen'] += 1
        self.towers.remove(tower)
        self.log("%s removed." % tower.to_json())
        self.stats['towers'] -= 1
        self.stats['towers_removed'] += 1
        return True

    def spawn(self, monster):
        self.stats['spawned'] += 1
        self.enemies.append(Enemy(len(self.walk)))
