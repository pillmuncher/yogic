# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

from collections import defaultdict
from itertools import starmap

from yogic import amb, predicate, resolve, seq, unify, var


@predicate
def equate(number, variables):
    return amb.from_iterable(unify((variable, number)) for variable in variables)

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
            ({a, b, c, e, h, i, j}, {2, 4, 5, 8, 10, 11, 12}),
            ({a, b, f, i, j, k, l}, {1, 4, 5, 6, 7, 8, 12}),
            ({a, c, d, e, f, k, l}, {1, 2, 6, 7, 8, 9, 10}),
            ({a, c, f, g, i, j, k}, {1, 2, 3, 4, 6, 8, 12}),
            ({b, c, d, e, f, g, h}, {1, 2, 3, 5, 9, 10, 11}),
            ({b, c, e, g, h, j, l}, {2, 3, 4, 5, 7, 10, 11}),
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
