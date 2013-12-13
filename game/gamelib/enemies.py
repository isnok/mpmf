
from random import random as rnd
from random import randint

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
