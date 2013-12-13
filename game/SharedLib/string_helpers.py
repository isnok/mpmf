import random
import string

def rndname(min_len=6, max_len=15, alphabet=string.ascii_letters):
    name = []
    for i in range(random.randint(min_len, max_len)):
        name.append(random.choice(alphabet))
    return "".join(name)

def ordinal(n):
    """ get ordinal of a number (positive integers) """

    end = n % 100
    if 4 <= end <= 20:
        return '%dth' % n

    end %= 10
    return ((end == 1) and '%sst'
         or (end == 2) and '%snd'
         or (end == 3) and '%srd'
         or                '%sth') % n
