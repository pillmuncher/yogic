Yet another Prolog-like thingy for Python. It's called yogic because logic programming is another step on the path to enlightenment. Just like yogic flying.

[![alt text](https://imgs.xkcd.com/comics/python.png "Flying")](https://xkcd.com/353)

# yogic.cs
**Yogic, but in C#.**


An embedded DSL of monadic combinators for first-order logic programming in Python.
It's called Yogic because logic programming is another step on the path to
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
def human(a):
    return unify_any(a, "socrates", "plato", "archimedes")

def dog(a):
    return unify_any(a, "fluffy", "daisy", "fifi")

def child(a, b):
    return amb(
        unify((a, "jim"), (b, "bob")),
        unify((a, "joe"), (b, "bob")),
        unify((a, "ian"), (b, "jim")),
        unify((a, "fifi"), (b, "fluffy")),
        unify((a, "fluffy"), (b, "daisy"))
    )

def descendant(a, c):
    b = var()
    return lambda subst: amb(
        child(a, c),
        seq(child(a, b), descendant(b, c))
    )(subst)

def mortal(a):
    b = var()
    return lambda subst: amb(
        human(a),
        dog(a),
        seq(descendant(a, b), mortal(b))
    )(subst)

def main():
    x = var()
    y = var()
    for subst in resolve(descendant(x, y)):
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

# Backtracking Monad-based Logic Programming in Python

This repository contains a Python implementation of a logic programming system using the Backtracking Monad approach. This approach allows you to express logical constraints and perform unification in a clean and structured manner.

## Core Concepts

### Success Function Type

A function type that represents a successful resolution. `Success` continuations are called with a substitution environment `subst` and a `Failure` continuation `backtrack`. They yield the provided substitution environment once and then yield whatever `backtrack()` yields.

### Failure Function Type

A function type that represents a failed resolution. `Failure` continuations are called to initiate backtracking.

### Ma Monad Type

The monad type. Combinators of this type take a `Success` continuation (`yes`) and two `Failure` continuations (`no` and `esc`). The `yes` continuation represents the current continuation, `no` represents the backtracking path, and `esc` is the escape continuation invoked by the `cut` combinator to jump out of the current computation back to the previous choice point.

### Mf Monadic Function Type

Combinators of this type take a substitution environment `subst` and return a monadic object.

### Combinators

- `bind(ma, mf)`: Applies the monadic computation `mf` to `ma` and returns the result. In the context of the backtracking monad, this means turning `mf` into a continuation.
- `unit(subst)`: Lifts a substitution environment `subst` into a computation. It succeeds once and then initiates backtracking.
- `cut(subst)`: Lifts a substitution environment `subst` into a computation. It succeeds once, and instead of normal backtracking, aborts the current computation and jumps to the previous choice point, effectively pruning the search space.
- `fail(subst)`: Lifts a substitution environment `subst` into a computation that never succeeds. It immediately initiates backtracking.
- `seq(*mfs)`: Composes multiple computations sequentially.
- `and_from_enumerable(mfs)`: Composes multiple computations sequentially from an enumerable.
- `amb(*mfs)`: Represents a choice between multiple computations. It takes a variable number of computations and returns a new computation that tries all of them in series with backtracking. This defines a *choice point*.
- `or_from_enumerable(mfs)`: Represents a choice between multiple computations from an enumerable. It takes a sequence of computations `mfs` and returns a new computation that tries all of them in series with backtracking. This defines a *choice point*.
- `not_(mf)`: Negates the result of a computation. It returns a new computation that succeeds if `mf` fails and vice versa.
- `unify(*pairs)`: Tries to unify pairs of objects. It fails if any pair is not unifiable.
- `unify_any(v, *os)`: Tries to unify a variable with any one of the objects. It fails if no object is unifiable.
- `resolve(goal)`: Perform logical resolution of the computation represented by `goal`.

### Usage

```python
# Example code showcasing the usage of the logic programming system
# ...

if __name__ == "__main__":
    main()

```csharp
public delegate Solutions Success(Subst subst, Failure backtrack)
```
- A function type that represents a successful resolution.  
  `Success` continuations are called with a substitution environment `subst`
  and a `Failure` continuation `backtrack` and yield the provided substitution
  environment once and then yield whatever `backtrack()` yields.

```csharp
public delegate Solutions Failure()
```
- A function type that represents a failed resolution.  
  `Failure` continuations are called to initiate backtracking.

```csharp
public delegate Solutions Ma(Success yes, Failure no, Failure esc)
```
- The monad type.  
  Combinators of this type take a `Success` continuation and two `Failure`
  continuations. The `yes` continuation represents the current continuation
  and `no` represents the backtracking path. `esc` is the escape continuation
  that is invoked by the `cut` combinator to jump out of the current
  comptutation back to the previous choice point. 

```csharp
public delegate Ma Mf(Subst subst)
```
- The monadic function type.  
  Combinators of this type take a substitution environment `subst` and
  return a monadic object.

```csharp
public static Ma bind(Ma ma, Mf mf)
```
- Applies the monadic computation `mf` to `ma` and returns the result.  
  In the context of the backtracking monad this means turning `mf` into a
  continuation.

```csharp
public static Ma unit(Subst subst)
```
- Lifts a substitution environment `subst` into a computation.  
  Succeeds once and then initates backtracking.

```csharp
public static Ma cut(Subst subst)
```
- Lifts a substitution environment `subst` into a computation.  
  Succeeds once, and instead of normal backtracking aborts the current
  computation and jumps to the previous choice point, effectively pruning the
  search space.

```csharp
public static Ma fail(Subst subst)
```
- Lifts a substitution environment `subst` into a computation.  
  Never succeeds. Immediately initiates backtracking.

```csharp
public static Mf then(Mf mf, Mf mg)
```
- Composes two computations sequentially.

```csharp
public static Mf and(params Mf[] mfs)
```
- Composes multiple computations sequentially.

```csharp
public static Mf and_from_enumerable(IEnumerable<Mf> mfs)
```
- Composes multiple computations sequentially from an enumerable.

```csharp
public static Mf choice(Mf mf, Mf mg)
```
- Represents a choice between two computations.  
  Takes two computations `mf` and `mg` and returns a new computation that tries
  `mf`, and if that fails, falls back to `mg`. This defines a *choice point*.

```csharp
public static Mf or(params Mf[] mfs)
```
- Represents a choice between multiple computations.  
  Takes a variable number of computations and returns a new computation that
  tries all of them in series with backtracking. This defines a *choice point*.

```csharp
public static Mf or_from_enumerable(IEnumerable<Mf> mfs)
```
- Represents a choice between multiple computations from an enumerable.  
  Takes a sequence of computations `mfs` and returns a new computation that
  tries all of them in series with backtracking. This defines a *choice point*.

```csharp
public static Mf not(Mf mf)
```
- Negates the result of a computation.  
  Returns a new computation that succeeds if `mf` fails and vice versa.

```csharp
public static Mf unify(params ValueTuple<object, object>[] pairs)
```
- Tries to unify pairs of objects. Fails if any pair is not unifiable.

```csharp
  public static Mf unify_any(Variable v, params object[] os) =>
```
- Tries to unify a variable with any one of objects. Fails if no object is unifiable.

```csharp
public static Solutions resolve(Mf goal)
```
- Perform logical resolution of the computation represented by `goal`.

```csharp
public class Variable
```
- Represents named logical variables.




```csharp
public delegate Solutions Success(Subst subst, Failure backtrack)
```
- A function type that represents a successful resolution.  
  `Success` continuations are called with a substitution environment `subst`
  and a `Failure` continuation `backtrack` and yield the provided substitution
  environment once and then yield whatever `backtrack()` yields.

```csharp
public delegate Solutions Failure()
```
- A function type that represents a failed resolution.  
  `Failure` continuations are called to initiate backtracking.

```csharp
public delegate Solutions Ma(Success yes, Failure no, Failure esc)
```
- The monad type.  
  Combinators of this type take a `Success` continuation and two `Failure`
  continuations. The `yes` continuation represents the current continuation
  and `no` represents the backtracking path. `esc` is the escape continuation
  that is invoked by the `cut` combinator to jump out of the current
  comptutation back to the previous choice point. 

```csharp
public delegate Ma Mf(Subst subst)
```
- The monadic function type.  
  Combinators of this type take a substitution environment `subst` and
  return a monadic object.

```csharp
public static Ma bind(Ma ma, Mf mf)
```
- Applies the monadic computation `mf` to `ma` and returns the result.  
  In the context of the backtracking monad this means turning `mf` into a
  continuation.

```csharp
public static Ma unit(Subst subst)
```
- Lifts a substitution environment `subst` into a computation.  
  Succeeds once and then initates backtracking.

```csharp
public static Ma cut(Subst subst)
```
- Lifts a substitution environment `subst` into a computation.  
  Succeeds once, and instead of normal backtracking aborts the current
  computation and jumps to the previous choice point, effectively pruning the
  search space.

```csharp
public static Ma fail(Subst subst)
```
- Lifts a substitution environment `subst` into a computation.  
  Never succeeds. Immediately initiates backtracking.

```csharp
public static Mf then(Mf mf, Mf mg)
```
- Composes two computations sequentially.

```csharp
public static Mf and(params Mf[] mfs)
```
- Composes multiple computations sequentially.

```csharp
public static Mf and_from_enumerable(IEnumerable<Mf> mfs)
```
- Composes multiple computations sequentially from an enumerable.

```csharp
public static Mf choice(Mf mf, Mf mg)
```
- Represents a choice between two computations.  
  Takes two computations `mf` and `mg` and returns a new computation that tries
  `mf`, and if that fails, falls back to `mg`. This defines a *choice point*.

```csharp
public static Mf or(params Mf[] mfs)
```
- Represents a choice between multiple computations.  
  Takes a variable number of computations and returns a new computation that
  tries all of them in series with backtracking. This defines a *choice point*.

```csharp
public static Mf or_from_enumerable(IEnumerable<Mf> mfs)
```
- Represents a choice between multiple computations from an enumerable.  
  Takes a sequence of computations `mfs` and returns a new computation that
  tries all of them in series with backtracking. This defines a *choice point*.

```csharp
public static Mf not(Mf mf)
```
- Negates the result of a computation.  
  Returns a new computation that succeeds if `mf` fails and vice versa.

```csharp
public static Mf unify(params ValueTuple<object, object>[] pairs)
```
- Tries to unify pairs of objects. Fails if any pair is not unifiable.

```csharp
  public static Mf unify_any(Variable v, params object[] os) =>
```
- Tries to unify a variable with any one of objects. Fails if no object is unifiable.

```csharp
public static Solutions resolve(Mf goal)
```
- Perform logical resolution of the computation represented by `goal`.

```csharp
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
