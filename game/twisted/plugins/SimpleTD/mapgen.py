from random import sample
from random import randint
from random import choice
from operator import itemgetter

tiles = ['spawn', 'walk', 'exit', 'free', 'blocked']
chars = {
    ' ': 'free',
    'S': 'spawn',
    'E': 'exit',
    'x': 'walk',
}

def gen_tile(char):
    string = chars[char]
    assert(string in tiles)
    return string

from twisted.python import log

def gen_map(x_size=32, y_size=34, w_len=100, c_cnt=9):
    """ generate x_size * y_size map with a
        way of len w_len and c_cnt corners.
    """

    rnd_corner = lambda where: (where, choice([-1,1]))
    _directions = {
            0: ( 1, 0),
            1: ( 0, 1),
            2: (-1, 0),
            3: ( 0,-1)
    }

    #_2squares = set()
    #for x in range(x_size - 1):
        #for y in range(y_size - 1):
            #_2squares.add(frozenset([(x, y), (x+1, y), (x, y+1), (x+1, y+1)]))

    def _3square(x,y):
        return frozenset([
            (x-1, y-1), (x, y-1), (x+1,y-1),
            (x-1, y  ), (x, y  ), (x+1,y  ),
            (x-1, y+1), (x, y+1), (x+1,y+1),
        ])

    _3squares = set()
    for x in range(1, x_size-1):
        for y in range(y_size-1):
            _3squares.add(_3square(x,y))

    def gen_walk(w_len, c_cnt):
        return map(rnd_corner, sample(range(w_len), c_cnt))

    generated = None
    tries = 0
    while not generated and tries < 1000:
        walk = sorted(gen_walk(w_len, c_cnt))
        _step = 0
        _x, _y = 0, 0
        _d = randint(0, 3)
        way = [ (_x, _y) ]
        tries += 1
        for corner in walk:
            if corner[0] - _step <= 1:
                continue
            _x = _x + _directions[_d][0] * (corner[0] - _step)
            _y = _y + _directions[_d][1] * (corner[0] - _step)
            way.append((_x, _y))
            _step = corner[0]
            _d = (_d + corner[1]) % 4
        _x = _x + _directions[_d][0] * (w_len - _step)
        _y = _y + _directions[_d][1] * (w_len - _step)
        way.append((_x, _y))

        _xl = min(way, key=itemgetter(0))[0]
        _xu = max(way, key=itemgetter(0))[0]

        _xs = _xu - _xl
        if _xs >= x_size + 2:
            continue

        _yl = min(way, key=itemgetter(1))[1]
        _yu = max(way, key=itemgetter(1))[1]

        _ys = _yu - _yl
        if _ys >= y_size + 2:
            continue

        log.msg("bounding box: %s x %s" % (_xs, _ys))

        x_o = (x_size - _xs) / 2 - _xl
        y_o = (y_size - _ys) / 2 - _yl

        log.msg("x_o = %s, y_o = %s" % (x_o, y_o))

        adjust = map(lambda c: (c[0] + x_o, c[1] + y_o), way)

        def flatten(c1,c2):
            x1, y1 = c1
            x2, y2 = c2
            if x1 == x2:
                if y1 < y2:
                    yvals = range(y1, y2)
                else:
                    yvals = range(y2+1, y1+1)[::-1]
                return [(x1, y) for y in yvals]
            elif y1 == y2:
                if x1 < x2:
                    xvals = range(x1, x2)
                else:
                    xvals = range(x2+1, x1+1)[::-1]
                return [(x, y1) for x in xvals]

        flattened = []
        flat_set = set()
        _pos = adjust.pop()
        while adjust:
            _new = adjust.pop()
            d = _pos[0] == _new[0]
            flat = flatten(_pos, _new)
            _coltmp = False
            for pos in flat:
                flat_set.add((pos, d))
            flattened.extend(flat)
            _pos = _new

        log.msg("Got walk: %s" % flattened)

        if not len(flat_set) == len(flattened):
            continue

        if any((len(s.intersection(flattened)) > 2 for s in (_3square(*x) for x in (flattened[0], flattened[-1])))):
            print "that just happened"
            continue

        if min(set().union(*flattened)) < 0:
            print "this just happened"
            continue

        if any((len(s.intersection(flattened)) > 5 for s in _3squares)):
            continue

        try:
            generated = [[ gen_tile(" ") for x in range(x_size) ] for y in range(y_size)]

            for x, y in flattened:
                generated[x][y] = gen_tile("x")

            generated[flattened[0][0]][flattened[0][1]] = gen_tile("S")
            generated[flattened[-1][0]][flattened[-1][1]] = gen_tile("E")

            print (2+x_size) * "#"
            for row in generated:
                #print "#" + "".join((tile['char'] for tile in row)) + "#"
                print "#" + "".join((tile[0] for tile in row)) + "#"
            print (2+x_size) * "#"
        except:
            generated = None

    if generated is not None:
        print "got a map after %s tries (len: %s, tiles: %s)" % (tries, len(flattened), len(flat_set))
    else:
        print "could not generate a map in 1000 tries!"
        import sys
        sys.exit(1)
    return generated, flattened

if __name__ == "__main__":
    gen_map()
