# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>

from yogic import *


@predicate
def child(a, b):
    return amb(
        unify([a, b], ['bob', 'archimedes']),
        unify([a, b], ['daisy', 'fluffy']),
        unify([a, b], ['fluffy', 'fifi']),
        unify([a, b], ['athene', 'zeus']),
    )


@predicate
def descendant(a, c):
    b = var()
    return amb(
        child(a, c),
        seq(child(a, b), descendant(b, c)),
    )

@predicate
def human(a):
    return amb(
        unify(a, 'socrates'),
        unify(a, 'plato'),
        unify(a, 'archimedes'),
    )

@predicate
def dog(a):
    return amb(
        unify(a, 'fifi'),
        unify(a, 'fluffy'),
        unify(a, 'daisy'),
    )

@predicate
def not_dog(a):
    return no(dog(a))

@predicate
def mortal(a):
    b = var()
    return amb(
        human(a),
        dog(a),
        seq(descendant(a, b), mortal(b)),
    )

@predicate
def append(a, b, c):
    x = var()
    y = var()
    z = var()
    return seq(
        unify([x, y], a),
        unify([y, z], b),
        unify([x, z], c),
    )


@predicate
def structure_unification(a, b, c):
    return seq(
        unify(a, [b, 2]),
        unify([1, c], a),
    )


# ----8<---------8<---------8<---------8<---------8<---------8<---------8<-----


x = var()
y = var()
z = var()


for each in resolve(seq(child(x, y), descendant(y, z))):
    print(each[x], each[y], each[z])
print()

for each in resolve(structure_unification(x, y, z)):
    print(each[x], each[y], each[z])
print()

for each in resolve(append([[1, 2, 3, x], x], [[4, 5, 6, y], y], [z, []])):
    print(each[x], each[y], each[z])
print()

for each in resolve(descendant(x, y)):
    print(each[x], each[y])
print()

for each in resolve(seq(mortal(x), not_dog(x))):
    print(each[x])
print()

for each in resolve(seq(not_dog(x), mortal(x))):
    print(each[x])
else:
    print('no.')
print()

for each in resolve(dog(x)):
    print(each[x])
else:
    print('no.')
print()

for each in resolve(no(dog(x))):
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

for each in resolve(amb()):
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
