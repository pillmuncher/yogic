#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.16a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

from itertools import permutations
from lib.yogic import *

def equate(letters, numbers):
    return alt(*[unify(letters, list(permutated_numbers))
                for permutated_numbers in permutations(numbers)])

# ----8<---------8<---------8<---------8<---------8<---------8<---------8<-----

a = var()
b = var()
c = var()
d = var()
e = var()
f = var()
h = var()
i = var()
j = var()

equation = seq(
        equate([b, f, i], [6, 10, 3]),
        equate([a, c, d, e, h], [2, 1, 9, 8, 4]),
        equate([d, e, h, i, j], [6, 4, 2, 5, 9]),
)

for n, each in enumerate(resolve(equation)):
    print('Ergebnis', n, '----------------------------------------------')
    print('a', each[a])
    print('b', each[b])
    print('c', each[c])
    print('d', each[d])
    print('e', each[e])
    print('f', each[f])
    print('h', each[h])
    print('i', each[i])
    print('j', each[j])
    print()
print()
