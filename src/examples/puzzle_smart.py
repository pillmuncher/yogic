# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

from collections import defaultdict
from itertools import starmap

from yogic import *


@predicate
def equate(number, variables):
    return alt.from_iterable(unify(variable, number) for variable in variables)

def simplify(puzzle):
    candidates = defaultdict(set)
    for variables, numbers in puzzle:
        for number in numbers:
            if number in candidates:
                candidates[number].intersection_update(variables)
            else:
                candidates[number].update(variables)
    return candidates.items()

# -----8<---------8<---------8<---------8<---------8<---------8<---------8<-----

a, b, c, d, e, f, g, h, i, j, k, l = (var() for _ in range(12))

puzzle = [
    ({a, d, e, f, j, k, l}, {2, 8, 6, 9, 1, 7, 4}),
    ({a, b, c, e, h, i, j}, {11, 1, 12, 8, 4, 5, 10}),
    ({b, c, d, e, f, g, h}, {5, 2, 9, 8, 11, 3, 10}),
    ({a, d, f, g, i, j, k}, {4, 6, 12, 1, 2, 9, 3}),
    ({b, c, g, h, j, l}, {3, 4, 7, 11, 5, 10}),
]

for n, each in enumerate(resolve(seq.from_iterable(starmap(equate, simplify(puzzle))))):
    print('Ergebnis', n, '----------------------------------------------')
    print('a', each[a])
    print('b', each[b])
    print('c', each[c])
    print('d', each[d])
    print('e', each[e])
    print('f', each[f])
    print('g', each[g])
    print('h', each[h])
    print('i', each[i])
    print('j', each[j])
    print('k', each[k])
    print('l', each[l])
    print()
print()
