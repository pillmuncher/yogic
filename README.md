# Yogic


An embedded DSL of monadic combinators for first-order logic programming in Python.

It's named Yogic because logic programming is another step on the path to
enlightenment.

[![alt text](https://imgs.xkcd.com/comics/python.png "Flying")](https://xkcd.com/353)

## **Key features:**

- **Horn Clauses as Functions**: Express logical facts and rules as simple
  functions.

- **Composable Combinators**: Define expressions of first-order logic by
  simply composing combinator functions.

- **Logical Variables**: Represented by the ``Variable`` class, they can be
  bound to arbitrary values including other variables during resolution.

- **Substitution and Unification**: The substitution environment provides
  variable bindings and is incrementally constructed during resolution. It
  is returned for each successful resolution.

- **Backtracking**: The monad combines the List and the Triple-Barrelled
  Continuation Monads for resolution, backtracking, and branch pruning via
  the ``cut`` combinator.

- **Algebraic Structures**: ``unit`` and ``then`` form a *Monoid* over
  monadic combinator functions, as do ``fail`` and ``choice``. Together they
  form a *Distributive Lattice* with ``then`` as the *meet* (infimum) and
  ``choice`` as the *join* (supremum) operator, and ``unit`` and ``fail`` as
  their respective identity elements. Because of the sequential nature of
  the employed resolution algorithm combined with the `cut`, the lattice is
  *non-commutative*.

## **A Motivating Example:**

We represent logical facts as functions that specify which individuals are
humans and dogs and define a `child(a, b)` relation such that `a` is the child
of `b`. Then we define rules that specify what a descendant and a mortal being
is. We then run queries that tell us which individuals are descendants of whom
and which individuals are both mortal and no dogs:
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
Note that `jim`, `bob`, `joe` and `ian` are not part of the result of the
second query because we didn't specify that they are human.

## **How it works:**

We interpret a function ``f(x1,...,xm) { return or(g1,...,gn); }``
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
example above, and return monadic functions of type ``Mf``, constructed by
composing your functions with the combinator functions provided by this
module, and start the resolution by giving an initial function, a so-called
*goal*, to ``resolve()`` and iterate over the results, one for each way *goal*
can be proven. No result means a failed resolution, that is the function
cannot be proven in the universe described by the given set of
functions/predicates.

## **API:**

```python
Subst = TypeVar('Subst')
```
- The type of the substitution environment that map variables to Values.

```python
Solutions = Iterable[Subst]
```
- ...

```python
Failure = Callable[[], Solutions]
```
- A function type that represents a failed resolution.  
  `Failure` continuations are called to initiate backtracking.

```python
Success = Callable[[Subst, Failure], Solutions]
```
- A function type that represents a successful resolution.  
  `Success` continuations are called with a substitution environment `subst`
  and a `Failure` continuation `backtrack` and yield the provided substitution
  environment once and then yield whatever `backtrack()` yields.

```python
Ma = Callable[[Success, Failure, Failure], Solutions]
```
- The monad type.  
  Combinators of this type take a `Success` continuation and two `Failure`
  continuations. The `yes` continuation represents the current continuation
  and `no` represents the backtracking path. `esc` is the escape continuation
  that is invoked by the `cut` combinator to jump out of the current
  comptutation back to the previous choice point. 

```python
Mf = Callable[[Subst], Ma]
```
- The monadic function type.  
  Combinators of this type take a substitution environment `subst` and
  return a monadic object.

```python
def bind(ma:Ma, mf:Mf) -> Ma
```
- Applies the monadic computation `mf` to `ma` and returns the result.  
  In the context of the backtracking monad this means turning `mf` into a
  continuation.

```python
def unit(subst:Subst) -> Ma
```
- Lifts a substitution environment `subst` into a computation.  
  Succeeds once and then initates backtracking.

```python
def cut(subst:Subst) -> Ma
```
- Lifts a substitution environment `subst` into a computation.  
  Succeeds once, and instead of normal backtracking aborts the current
  computation and jumps to the previous choice point, effectively pruning the
  search space.

```python
def fail(subst.Subst) -> Ma
```
- Lifts a substitution environment `subst` into a computation.  
  Never succeeds. Immediately initiates backtracking.

```python
def then(mf:Mf, mg:Mf) -> Mf
```
- Composes two computations sequentially.

```python
def seq(*mfs:Mf) -> Mf
```
- Composes multiple computations sequentially.

```python
def seq.from_enumerable(mfs:Sequence[Mf]) -> Mf
```
- Composes multiple computations sequentially from an enumerable.

```python
def choice(mf:Mf, mg:Mf) -> Mf
```
- Represents a choice between two computations.  
  Takes two computations `mf` and `mg` and returns a new computation that tries
  `mf`, and if that fails, falls back to `mg`. This defines a *choice point*.

```python
def amb(*mfs:Mf) -> Mf
```
- Represents a choice between multiple computations.  
  Takes a variable number of computations and returns a new computation that
  tries all of them in series with backtracking. This defines a *choice point*.

```python
def amb.from_enumerable(mfs:Sequence[Mf]) -> Mf
```
- Represents a choice between multiple computations from an enumerable.  
  Takes a sequence of computations `mfs` and returns a new computation that
  tries all of them in series with backtracking. This defines a *choice point*.

```python
def not(mf:Mf) -> Mf
```
- Negates the result of a computation.  
  Returns a new computation that succeeds if `mf` fails and vice versa.

```python
def unify(...) -> Mf
```
- Tries to unify pairs of objects. Fails if any pair is not unifiable.

```python
def unify_any(Variable v, *objects) -> Mf
```
- Tries to unify a variable with any one of objects. Fails if no object is unifiable.

```python
def resolve(goal:Mf) -> Solutions
```
- Perform logical resolution of the computation represented by `goal`.

```python
public class Variable
```
- Represents named logical variables.

## Links:

Unification:  
https://eli.thegreenplace.net/2018/unification/

Backtracking:  
https://en.wikipedia.org/wiki/Backtracking

Logical Resolution:  
http://web.cse.ohio-state.edu/~stiff.4/cse3521/logical-resolution.html

Horn Clauses:  
https://en.wikipedia.org/wiki/Horn_clause

Monoid:  
https://en.wikipedia.org/wiki/Monoid

Distributive Lattice:  
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
