
from random import random as rnd
from random import randint
from twisted.internet import reactor

class Tower:

    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.area = set()
        for dx in range(-3,4):
            for dy in range(-3,4):
                self.area.add((self.x+dx, self.y+dy))
        self.shoot = None
        self.cooldown = False

    def to_json(self):
        return {'x': self.x, 'y': self.y}
            #'shoots': sorted(self.area)}

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
                msg.append((enemy.id, enemy.at, dmg))
            #log.msg("(%s,%s) dmg stats: %s" % (self.x, self.y, msg))
            self.cooldown = True
            reactor.callLater(0.7, self.unfreeze)

    def unfreeze(self):
        self.cooldown = False

    def enemy_coord_idx(self, enemy):
        return int(round(enemy.at))
