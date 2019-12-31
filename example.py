#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.4a'
__date__ = '2020-01-01'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

import time

from lib.yogic import (and_then, bind, either, nothing, recursive, resolve,
                       unify, unit, var)


def human(a):
    return either(
        unify(a, 'socrates'),
        unify(a, 'plato'),
        unify(a, 'bob'),
    )

def dog(a):
    return unify(a, 'fifi')

def child(a, b):
    return either(
        unify([a, b], ['archimedes', 'bob']),
        unify([a, b], ['fluffy', 'fifi']),
        unify([a, b], ['daisy', 'fluffy']),
        unify([a, b], ['athene', 'zeus']),
    )

@recursive
def descendant(a, c):
    b = var()
    return either(
        child(a, c),
        and_then(child(a, b), descendant(b, c)),
    )

def mortal(a):
    b = var()
    return either(
        human(a),
        dog(a),
        and_then(descendant(a, b), either(human(b), dog(b))),
    )

def append(a, b, c):
    x = var()
    y = var()
    z = var()
    return and_then(
        unify([x, y], a),
        unify([y, z], b),
        unify([x, z], c),
    )

# ----8<---------8<---------8<---------8<---------8<---------8<---------8<-----


x = var()
y = var()
z = var()
_ = var()


for each in resolve(append([[1, 2, 3, x], x],
                           [[4, 5, 6, y], y],
                           [z, []])):
    print('yes.')
    print(each[x])
    print(each[y])
    print(each[z])
else:
    print('no.')


for each in resolve(and_then(dog(y), child(x, y))):
    print(each[x], each[y])
    print('yes.')
    break
else:
    print('no.')
for each in resolve(and_then(dog(y), descendant(x, y))):
    print('yes.')
    print(each[x], each[y])
    break
else:
    print('no.')
for each in resolve(and_then(child(x, y), descendant(y, z))):
    print('yes.')
    print(each[x], each[y], each[z])
else:
    print('no.')
for each in resolve(mortal(x)):
    print(each[x])
print()
for each in resolve(mortal('archimedes')):
    print('yes.')
print()
for each in resolve(mortal('joe')):
    print('yes.')
else:
    print('no.')
print()
for each in resolve(unify([x, y, 'huhu'], [y, z, x])):
    print('yes.')
    print(each[x])
    print(each[y])
    print(each[z])
else:
    print('no.')

for each in resolve(bind(dog(x), unit)):
    print(each[x])

for each in resolve(bind(unit, dog(x))):
    print(each[x])

for each in resolve(bind(bind(mortal(x), dog(y)), child(x, y))):
    print(each[x])

for each in resolve(bind(mortal(x), bind(dog(y), child(x, y)))):
    print(each[x])
