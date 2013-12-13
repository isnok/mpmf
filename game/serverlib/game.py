from twisted.python import log
from serverlib.jsonhttp import JsonResource

from gamelib.mapgen import gen_map
from gamelib.enemies import Enemy
from gamelib.towers import Tower

from twisted.application.service import Service
from twisted.internet.task import LoopingCall

from random import randint

from collections import defaultdict

class GameBackend(Service):

    def __init__(self, world, name):
        self.world = world
        self.name = name

        tilemap, enemywalk = gen_map()
        self.map = tilemap
        self.walk = enemywalk
        self.start = enemywalk[0]
        self.end = enemywalk[1]

        self.enemies = []
        self.towers = []
        self.stats = defaultdict(int)

        self.tick = 0
        self.runInterval = 0.1
        self.runLoop = LoopingCall(self.update)

    def startService(self):
        if not self.running:
            log.msg("Game %s started." % self.name)
            Service.startService(self)
            self.runLoop.start(self.runInterval)

    def stopService(self):
        if self.running:
            log.msg("Game %s paused." % self.name)
            Service.stopService(self)
            self.runLoop.stop()

    def toggleRunning(self):
        if self.running:
            self.stopService()
        else:
            self.startService()

    def render_GET(self, request):
        return "There are %d enemies on the field." % len(self.enemies)

    def getChild(self, name, request):
        if name == '':
            return self
        elif name == 'map':
            return JsonResource(name, self.map)
        elif name == 'walk':
            return JsonResource(name, self.walk)
        elif name == 'enemies':
            return JsonResource(name, [ e.to_json() for e in self.enemies ])
        elif name == 'towers':
            return JsonResource(name, [ t.to_json() for t in self.towers ])
        elif name == 'pause':
            self.toggleRunning()
            return JsonResource(name, self.running)
        else:
            return JsonResource(name, 'page does not exist')

    def update(self):
        if not self.running:
            return

        #if not (self.tick % 20):
            #self.say("%s enemies on the field." % len(self.enemies))

        self.tick += 1
        if not randint(0,3):
            self.spawn("painin sias")

        for t in self.towers:
            t.update(self.runInterval)

        dead = []
        for enemy in self.enemies:
            died = enemy.update(self.runInterval)
            if died:
                dead.append((died, enemy))

        for (reason, d) in dead:
            try:
                self.enemies.remove(d)
                #log.msg("%s: %s" % (reason, d.to_json()))
                self.stats[reason] += 1
            except:
                pass

    def place_tower(self, x, y):
        self.remove_tower(x, y)
        if self.map[x][y] == 'free':
            self.towers.append(Tower(self, x, y))
            log.msg("Tower built at (%s,%s)." % (x,y))
            self.stats['towers'] += 1
            return True
        else:
            return False

    def remove_tower(self, x, y):
        try:
            towers = filter(lambda t: t.x == x and t.y == y, self.towers)
            if not towers:
                return
            else:
                tower = towers.pop()
            self.towers.remove(tower)
            log.msg("%s removed." % tower.to_json())
            self.stats['towers'] -= 1
            return True
        except:
            return False

    def spawn(self, monster):
        self.stats['spawned'] += 1
        self.enemies.append(Enemy(len(self.walk)))
