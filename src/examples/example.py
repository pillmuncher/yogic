# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

__version__ = '0.2.3'
__date__ = '2021-04-22'
__author__ = 'Mick Krippendorf <m.krippendorf@freenet.de>'
__license__ = 'MIT'

from yogic import *


@predicate
def human(a):
    return staralt(
        unify(a, 'socrates'),
        unify(a, 'plato'),
        unify(a, 'bob'),
    )

@predicate
def dog(a):
    return staralt(
        unify(a, 'fifi'),
        unify(a, 'fluffy'),
        unify(a, 'daisy'),
    )

@predicate
def not_dog(a):
    return no(dog(a))

@predicate
def child(a, b):
    return staralt(
        unify([a, b], ['archimedes', 'bob']),
        unify([a, b], ['fluffy', 'fifi']),
        unify([a, b], ['daisy', 'fluffy']),
        unify([a, b], ['athene', 'zeus']),
    )

@predicate
def descendant(a, c):
    b = var()
    return staralt(
        child(a, c),
        starseq(child(a, b), descendant(b, c)),
    )

@predicate
def mortal(a):
    b = var()
    return staralt(
        human(a),
        dog(a),
        starseq(descendant(a, b), mortal(b)),
    )

@predicate
def append(a, b, c):
    x = var()
    y = var()
    z = var()
    return starseq(
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

for each in resolve(starseq(child(x, y), descendant(y, z))):
    print(each[x], each[y], each[z])
print()

for each in resolve(starseq(mortal(x), not_dog(x))):
    print(each[x])
print()

for each in resolve(starseq(not_dog(x), mortal(x))):
    print(each[x])
else:
    print('no.')
print()

for each in resolve(starseq()):
    print('yes.')
    break
else:
    print('no.')
print()

for each in resolve(staralt()):
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

for each in resolve(starseq(unify(x, 1), unify(y, 2))):
    print(each[x], each[y])
print()

for each in resolve(unify([x, y, 'test'], [y, z, x])):
    print(each[x], each[y], each[z])
print()
