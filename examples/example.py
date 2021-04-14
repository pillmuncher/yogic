# Copyright (c) 2020 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.18a'
__date__ = '2020-04-13'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

from yogic import *


def human(a):
    return alt(
        unify(a, 'socrates'),
        unify(a, 'plato'),
        unify(a, 'bob'),
    )

def dog(a):
    return alt(
        unify(a, 'fifi'),
        unify(a, 'fluffy'),
        unify(a, 'daisy'),
    )

def not_dog(a):
    return no(dog(a))

def child(a, b):
    return alt(
        unify([a, b], ['archimedes', 'bob']),
        unify([a, b], ['fluffy', 'fifi']),
        unify([a, b], ['daisy', 'fluffy']),
        unify([a, b], ['athene', 'zeus']),
    )

@recursive
def descendant(a, c):
    b = var()
    return alt(
        child(a, c),
        seq(child(a, b), descendant(b, c)),
    )

@recursive
def mortal(a):
    b = var()
    return alt(
    human(a),
    dog(a),
    seq(descendant(a, b), mortal(b)),
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

for each in resolve(seq(not_dog(x), mortal(x))):
    print(each[x])
else:
    print('no.')
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
    print('yes.')
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
