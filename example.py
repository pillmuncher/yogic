#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.12a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

from lib import identity
from lib.yogic import *


def human(a):
    return alt(
        unify(a, 'socrates'),
        unify(a, 'plato'),
        unify(a, 'bob'),
    )

def dog(a):
    return unify(a, 'fifi')

def not_dog(a):
    return no(dog(a))

@predicate
def child(a, b):
    yield unify([a, b], ['archimedes', 'bob'])
    yield unify([a, b], ['fluffy', 'fifi'])
    yield unify([a, b], ['daisy', 'fluffy'])
    yield unify([a, b], ['athene', 'zeus'])

@recursive
def descendant(a, c):
    b = var()
    return alt(
        child(a, c),
        seq(child(a, b), descendant(b, c)),
    )

def mortal(a):
    b = var()
    return alt(
        human(a),
        dog(a),
        seq(descendant(a, b), alt(human(b), dog(b))),
    )

def append(a, b, c):
    x = var()
    y = var()
    z = var()
    return seq(
        unify([x, y], a),
        unify([y, z], b),
        unify([x, z], c),
    )

# ----8<---------8<---------8<---------8<---------8<---------8<---------8<-----


x = var()
y = var()
z = var()


for each in resolve(append([[1, 2, 3, x], x], [[4, 5, 6, y], y], [z, []])):
    print(each[x], each[y], each[z])
print()

for each in resolve(descendant(x, y)):
    print(each[x], each[y])
print()

for each in resolve(seq(child(x, y), descendant(y, z))):
    print(each[x], each[y], each[z])
print()

for each in resolve(seq(mortal(x), not_dog(x))):
    print(each[x])
print()

for each in resolve(seq()):
    print('yes.')
    break
else:
    print('no.')
print()

for each in resolve(alt()):
    print('yes.')
    break
else:
    print('no.')
print()

for each in resolve(mortal('archimedes')):
    break
else:
    print('no.')
print()

for each in resolve(mortal('joe')):
    break
else:
    print('no.')
print()

for each in resolve(seq(unify(x, 1), unify(y, 2))):
    print(each[x], each[y])
print()

for each in resolve(unify([x, y, 'test'], [y, z, x])):
    print(each[x], each[y], each[z])
print()

for each in resolve(bind(dog(x), unit)):
    print(each[x])
print()

for each in resolve(bind(unit, dog(x))):
    print(each[x])
print()

for each in resolve(bind(bind(mortal(x), dog(y)), child(x, y))):
    print(each[x])
print()

for each in resolve(bind(mortal(x), bind(dog(y), child(x, y)))):
    print(each[x])
print()
