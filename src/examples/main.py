from yogic import *

def human(a):   # socrates, plato, and archimedes are human
    return unify_any(a, "socrates", "plato", "archimedes")

def dog(a):     # fluffy, daisy, and fifi are dogs
    return unify_any(a, "fluffy", "daisy", "fifi")

def child(a, b):
    return amb(
        seq(unify(a, "jim"), unify(b, "bob")),      # jim is a child of bob.
        seq(unify(a, "joe"), unify(b, "bob")),      # joe is a child of bob.
        seq(unify(a, "ian"), unify(b, "jim")),      # ian is a child of jim.
        seq(unify(a, "fifi"), unify(b, "fluffy")),  # fifi is a child of fluffy.
        seq(unify(a, "fluffy"), unify(b, "daisy"))  # fluffy is a child of daisy.
    )

def descendant(a, c):
    b = var()
    # by returning a lambda function we
    # create another level of indirection,
    # so that the recursion doesn't
    # immediately trigger an infinite loop
    # and cause a stack overflow:
    return lambda subst: amb(               # a is a descendant of c iff:
        child(a, c),                        # a is a child of c, or
        seq(child(a, b), descendant(b, c))  # a is a child of b and b is b descendant of c.
    )(subst)

def mortal(a):
    b = var()
    return lambda subst: amb(               # a is mortal iff:
        human(a),                           # a is human, or
        dog(a),                             # a is a dog, or
        seq(descendant(a, b), mortal(b))    # a descends from a mortal.
    )(subst)

def main():
    x = var()
    y = var()
    for subst in resolve(child(x, y)):
        print(f"{subst[x]} is a descendant of {subst[y]}.")
    print()
    for subst in resolve(seq(mortal(x), no(dog(x)))):
        print(f"{subst[x]} is mortal and no dog.")


if __name__ == "__main__":
    main()
