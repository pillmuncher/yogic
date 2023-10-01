# Copyright (c) 2021 Mick Krippendorf <m.krippendorf@freenet.de>
from itertools import permutations

from yogic import amb, predicate, resolve, seq, unify, var


@predicate
def equate(letters, numbers):
    return amb.from_iterable(
        unify(*zip(list(letters), list(permutation)))
        for permutation in permutations(numbers)
    )


# -----8<---------8<---------8<---------8<---------8<---------8<---------8<-----

a, b, c, d, e, f, g, h, i, j, k, l = (var() for _ in range(12))

puzzle = seq(
    equate({a, b, c, e, h, i, j}, {2, 4, 5, 8, 10, 11, 12}),
    equate({a, b, f, i, j, k, l}, {1, 4, 5, 6, 7, 8, 12}),
    equate({a, c, d, e, f, k, l}, {1, 2, 6, 7, 8, 9, 10}),
    equate({a, c, f, g, i, j, k}, {1, 2, 3, 4, 6, 8, 12}),
    equate({b, c, d, e, f, g, h}, {1, 2, 3, 5, 9, 10, 11}),
    equate({b, c, e, g, h, j, l}, {2, 3, 4, 5, 7, 10, 11}),
)

for n, each in enumerate(resolve(puzzle)):
    print("Ergebnis", n, "----------------------------------------------")
    print("a", each[a])
    print("b", each[b])
    print("c", each[c])
    print("d", each[d])
    print("e", each[e])
    print("f", each[f])
    print("g", each[g])
    print("h", each[h])
    print("i", each[i])
    print("j", each[j])
    print("k", each[k])
    print("l", each[l])
    print()
print()
