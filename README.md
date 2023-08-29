# Yogic
An embedded DSL of monadic combinators for first-order logic programming in Python.


It's named Yogic because logic programming is another step on the path
to enlightenment.

[![alt text](https://imgs.xkcd.com/comics/python.png "Flying")](https://xkcd.com/353)

## **Key features:**

- **Horn Clauses as Functions**: Express logical facts and rules as
  simple functions.

- **Composable Combinators**: Define expressions of first-order logic by
  simply composing combinator functions.

- **Logical Variables**: Represented by the ``Variable`` class, they can
  be bound to arbitrary values including other variables during
  resolution.

- **Substitution and Unification**: The substitution environment
  provides variable bindings and is incrementally constructed during
  resolution. It is returned for each successful resolution.

- **Backtracking**: The monad combines the List and the Triple-Barrelled
  Continuation Monads for resolution, backtracking, and branch pruning
  via the ``cut`` combinator.

- **Algebraic Structures**: ``unit`` and ``then`` form a *Monoid* over
  monadic combinator functions, as do ``fail`` and ``choice``. Together
  they form a *Distributive Lattice* with ``then`` as the *meet*
  (infimum) and ``choice`` as the *join* (supremum) operator, and
  ``unit`` and ``fail`` as their respective identity elements. Because
  of the sequential nature of the employed resolution algorithm combined
  with the `cut`, the lattice is *non-commutative*.

## **A Motivating Example:**

We represent logical facts as functions that specify which individuals
are humans and dogs and define a `child(a, b)` relation such that `a` is
the child of `b`. Then we define rules that specify what a descendant
and a mortal being is. We then run queries that tell us which
individuals are descendants of whom and which individuals are both
mortal and no dogs:
```python
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
```
**Result:**
```
jim is a descendant of bob.
joe is a descendant of bob.
ian is a descendant of jim.
fifi is a descendant of fluffy.
fluffy is a descendant of daisy.
ian is a descendant of bob.
fifi is a descendant of daisy.

socrates is mortal and no dog.
plato is mortal and no dog.
archimedes is mortal and no dog.
```
Note that `jim`, `bob`, `joe` and `ian` are not part of the result of
the second query because we didn't specify that they are human.

## **How it works:**

We interpret a function ``f(x1,...,xm) { return amb(g1,...,gn); }``
as a set of logical implications:

```
g1  ⟶  f(x1,...,xm)
...
gn  ⟶  f(x1,...,xm)
```

We call ``f(x1,...,xn)`` the *head* and each ``gi`` a *body*.

We prove these by *modus ponens*:

```
A  ⟶  B            gi  ⟶  f(x1,...,xn)
A                  gi
⎯⎯⎯⎯⎯          ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
B                  f(x1,...,xn)
```

A function with head ``f(x1,...,xm)`` is proven by proving any of
``g1,...gn`` recursively. When we reach a success goal that has no body,
there's nothing left to prove. This process is called a *resolution*.

## **How to use it:**

Just write functions that take in Variables and other values like in the
example above, and return monadic functions of type ``Mf``, constructed
by composing your functions with the combinator functions provided by
this module, and start the resolution by giving an initial function, a
so-called *goal*, to ``resolve()`` and iterate over the results, one for
each way *goal* can be proven. No result means a failed resolution, that
is the function cannot be proven in the universe described by the given
set of functions/predicates.

## **API:**

```python
Subst = TypeVar('Subst')
```
- The type of the substitution environment that maps variables to values.

```python
Solutions = Iterable[Subst]
```
- A sequence of substitution environments, one for each solution for a
  logical query.

```python
Failure = Callable[[], Solutions]
```
- A function type that represents a failed resolution.
  `Failure` continuations are called to initiate backtracking.

```python
Success = Callable[[Subst, Failure], Solutions]
```
- A function type that represents a successful resolution.
  `Success` continuations are called with a substitution environment of
  type `Subst` and a `Failure` continuation for backtackiing. They first
  yield the provided substitution environment once and then yield
  whatever the `Failure` continuation yields.

```python
Ma = Callable[[Success, Failure, Failure], Solutions]
```
- The monadic computation type.
  Combinators of this type take a `Success` continuation and two
  `Failure` continuations. The `Success` continuation represents the
  current continuation The first `Failure` continuation represents the
  backtracking path. The second `Failure` Continuation is the escape
  continuation that is invoked by the `cut` combinator to jump out of
  the current comptutation back to the previous choice point.

```python
Mf = Callable[[Subst], Ma]
```
- The monadic continuation type.
  Combinators of this type take a substitution environment of type
  `Subst` and return a monadic object.

```python
bind(ma:Ma, mf:Mf) -> Ma
```
- Applies the monadic continuation `mf` to `ma` and returns the result.
  In the context of the backtracking monad this means turning `mf` into
  the continuation of the computation `ma`.

```python
unit(subst:Subst) -> Ma
```
- Takes a substitution environment `subst` into a monadic computation.
  Succeeds once and then initates backtracking.

```python
cut(subst:Subst) -> Ma
```
- Takes a substitution environment `subst` into a monadic computation.
  Succeeds once, and instead of normal backtracking aborts the current
  computation and jumps to the previous choice point, effectively
  pruning the search space.

```python
fail(subst:Subst) -> Ma
```
- Takes a substitution environment `subst` into a monadic computation.
  Never succeeds. Immediately initiates backtracking.

```python
then(mf:Mf, mg:Mf) -> Mf
```
- Composes two monadic continuations sequentially.

```python
seq(*mfs:Mf) -> Mf
```
- Composes multiple monadic continuations sequentially.

```python
seq.from_iterable(mfs:Sequence[Mf]) -> Mf
```
- Composes multiple monadic continuations sequentially from an iterable.

```python
choice(mf:Mf, mg:Mf) -> Mf
```
- Represents a choice between two monadic continuations.
  Takes two continuations `mf` and `mg` and returns a new continuation
  that tries `mf`, and if that fails, falls back to `mg`.
  This defines a *choice point*.

```python
amb(*mfs:Mf) -> Mf
```
- Represents a choice between multiple monadic continuations.
  Takes a variable number of continuations and returns a new
  continuation that tries all of them in series with backtracking.
  This defines a *choice point*.

```python
amb.from_iterable(mfs:Sequence[Mf]) -> Mf
```
- Represents a choice between multiple monadic continuations from an
  iterable.
  Takes a sequence of continuations `mfs` and returns a new continuation
  that tries all of them in series with backtracking.
  This defines a *choice point*.

```python
not(mf:Mf) -> Mf
```
- Negates the result of a monadic continuation.
  Returns a new continuation that succeeds if `mf` fails and vice versa.

```python
unify(this:Any, that:Any) -> Mf
```
- Tries to unify pairs of objects. Fails if any pair is not unifiable.

```python
unify_any(Variable v, *objects:Any) -> Mf
```
- Tries to unify a variable with any one of objects.
  Fails if no object is unifiable.

```python
resolve(goal:Mf) -> Solutions
```
- Perform logical resolution of the monadic continuation represented by
  `goal`.

```python
class Variable
```
- Represents logical variables.

## Links:

Unification:
https://eli.thegreenplace.net/2018/unification/

Backtracking:
https://en.wikipedia.org/wiki/Backtracking

Logical Resolution:
http://web.cse.ohio-state.edu/~stiff.4/cse3521/logical-resolution.html

Horn Clauses:
https://en.wikipedia.org/wiki/Horn_clause

Monoids:
https://en.wikipedia.org/wiki/Monoid

Distributive Lattices:
https://en.wikipedia.org/wiki/Distributive_lattice

Monads:
https://en.wikipedia.org/wiki/Monad_(functional_programming)

Monads Explained in C# (again):
https://mikhail.io/2018/07/monads-explained-in-csharp-again/

Discovering the Continuation Monad in C#:
https://functionalprogramming.medium.com/deriving-continuation-monad-from-callbacks-23d74e8331d0

Continuations:
https://en.wikipedia.org/wiki/Continuation

Continuations Made Simple and Illustrated:
https://www.ps.uni-saarland.de/~duchier/python/continuations.html

The Discovery of Continuations:
https://www.cs.ru.nl/~freek/courses/tt-2011/papers/cps/histcont.pdf
