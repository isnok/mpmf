
tiles = ['spawn', 'walk', 'exit', 'free', 'blocked']

walkable = [ 'spawn', 'walk', 'exit' ]
buildable = [ 'free' ]

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
    #return {
        #'name': string,
        #'char': char,
        #'walk': string in walkable,
        #'build': string in buildable,
    #}
