# Yogic

**An embedded DSL of monadic combinators for first-order logic programming in Python.**

It's called Yogic because logic programming is another step on the path to
enlightenment.

[![alt text](https://imgs.xkcd.com/comics/python.png "Flying")](https://xkcd.com/353)

## **Key features:**

* **Horn Clauses as Composable Combinators**: Define facts and rules of
  first-order logic by simply composing combinator functions.

* **Unification, Substitution, and Logical Variables**: The substitution
  environment provides Variable bindings and is incrementally constructed
  during resolution through the Unification operation. It is returned for each
  successful resolution.

* **Backtracking and the Cut**: Internally, the code uses the Triple-Barrelled
  Continuation Monad for resolution, backtracking, and branch pruning via the
  `cut` combinator.

## **An Example:**

We represent logical facts as functions that specify which individuals are
humans and dogs and define a `child(a, b)` relation such that `a` is the child
of `b`. Then we define rules that specify what a descendant and a mortal being
is. We then run queries that tell us which individuals are descendants of whom
and which individuals are both mortal and no dogs:

```python
from yogic import *

def human(a):                               # socrates, plato, and archimedes are human
    return unify_any(a, "socrates", "plato", "archimedes")

def dog(a):                                 # fluffy, daisy, and fifi are dogs
    return unify_any(a, "fluffy", "daisy", "fifi")

def child(a, b):
    return amb(
        unify((a, "jim"), (b, "bob")),      # jim is a child of bob.
        unify((a, "joe"), (b, "bob")),      # joe is a child of bob.
        unify((a, "ian"), (b, "jim")),      # ian is a child of jim.
        unify((a, "fifi"), (b, "fluffy")),  # fifi is a child of fluffy.
        unify((a, "fluffy"), (b, "daisy"))  # fluffy is a child of daisy.
    )

@predicate
def descendant(a, c):
    b = var()
    return amb(                             # a is a descendant of c iff:
        child(a, c),                        # a is a child of c, or
        seq(child(a, b), descendant(b, c))  # a is a child of b and b is a descendant of c.
    )

@predicate
def mortal(a):
    b = var()
    return amb(                             # a is mortal iff:
        human(a),                           # a is human, or
        dog(a),                             # a is a dog, or
        seq(descendant(a, b), mortal(b))    # a descends from a mortal.
    )

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
second query because we didn't specify that they are human. Also note that the
third query doesn't produce any solutions, because in the clause `not(dog(x))`
the variable `x` isn't bound yet. Unbound variables are implicitely
∀-quantified and by saying `not(dog(x))` we're saying that nothing is a dog,
which in the universe we defined is not true.

## **How it works:**

We interpret a function `f(x1,...,xm) { return or(g1,...,gn); }`
as a set of logical implications:

```
g1  ⟶  f(x1,...,xm)
...
gn  ⟶  f(x1,...,xm)
```

We call `f(x1,...,xm)` the *head* and each `gi` a *body*.

We prove these by *modus ponens*:

```
A  ⟶  B            gi  ⟶  f(x1,...,xm)
A                  gi
⎯⎯⎯⎯⎯          ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
B                  f(x1,...,xm)
```

A function with head `f(x1,...,xm)` is proven by proving any of
`g1,...,gn` recursively. When we reach a goal that has no body, there's
nothing left to prove. This process is called a *resolution*.

## **How to use it:**

Just write functions that take in Variables and other values like in the
example above, and return combinator functions of type `Goal`, constructed
by composing your functions with the combinator functions provided by this
module, and start the resolution by giving an initial function, a so-called
*goal*, to `resolve()` and iterate over the results, one for each way *goal*
can be proven. No result means a failed resolution, that is the function
cannot be proven in the universe described by the given set of
functions/predicates.

## **API:**

```python
Subst = TypeVar('Subst') XXX
```

* The type of the substitution environment that maps variables to values.

```python
Solutions = Iterable[Subst] XXX
```

* A sequence of substitution environments, one for each solution for a
  logical query.

```python
Result = Optional[tuple[Solutions, Next]]
```

* A structure representing the current solution and the next continuation to
  invoke.
  Needed for Tail Call Elimination.

```python
Next = Callable[[], Result]
```

* A function type that represents a backtracking operation.

```python
Emit = Callable[[Subst, Next], Result]
```

* A function type that represents a successful resolution.

```python
Step = Callable[[Emit, Next, Next], Result]
```

* A function type that represents a resolution step.

```python
Goal = Callable[[Subst], Step]
```

* A function type that represents a resolvable logical statement.

```python
unit(subst:Subst) -> Step
```

* Takes a substitution environment `subst` into a computation.\
  Succeeds once and then initates backtracking.

```python
cut(subst:Subst) -> Step
```

* Takes a substitution environment `subst` into a monadic computation.
  Succeeds once, and instead of normal backtracking aborts the current
  computation and jumps to the previous choice point, effectively
  pruning the search space.

```python
fail(subst:Subst) -> Step
```

* Takes a substitution environment `subst` into a monadic computation.
  Never succeeds. Immediately initiates backtracking.

```python
then(goal1:Goal, goal1:Goal) -> Goal
```

* Composes two monadic continuations sequentially.

```python
seq(*goals:Goal) -> Goal
```

* Composes multiple monadic continuations sequentially.

```python
seq.from_iterable(goals:Sequence[Goal]) -> Goal
```

* Composes multiple monadic continuations sequentially from an iterable.

```python
choice(goal1:Goal, goal1:Goal) -> Goal
```

* Represents a choice between two monadic continuations.
  Takes two continuations `goal` and `goal1` and returns a new continuation
  that tries `goal`, and if that fails, falls back to `goal1`.
  This defines a *choice point*.

```python
amb(*goals:Goal) -> Goal
```

* Represents a choice between multiple monadic continuations.
  Takes a variable number of continuations and returns a new
  continuation that tries all of them in series with backtracking.
  This defines a *choice point*.

```python
amb.from_iterable(goals:Sequence[Goal]) -> Goal
```

* Represents a choice between multiple monadic continuations from an iterable.
  Takes a sequence of continuations `goals` and returns a new continuation
  that tries all of them in series with backtracking.
  This defines a *choice point*.

```python
no(goal:Goal) -> Goal
```

* Negates the result of a monadic continuation.
  Returns a new continuation that succeeds if `goal` fails and vice versa.

```python
unify(this:Any, that:Any) -> Goal
```

* Tries to unify pairs of objects.
  Fails if any pair is not unifiable.

```python
unify_any(v:Variable, *objects:Any) -> Goal
```

* Tries to unify a variable with any one of objects.
  Fails if no object is unifiable.

```python
resolve(goal:Goal) -> Solutions
```

* Perform logical resolution of the monadic continuation represented by
  `goal`.

```python
class Variable
```

* Represents logical variables.

## Links:

Unification:
https://eli.thegreenplace.net/2018/unification/

Backtracking:
https://en.wikipedia.org/wiki/Backtracking

Logical Resolution:
http://web.cse.ohio-state.edu/~stiff.4/cse3521/logical-resolution.html

Horn Clauses:
https://en.wikipedia.org/wiki/Horn\_clause

Monoids:
https://en.wikipedia.org/wiki/Monoid

Distributive Lattices:
https://en.wikipedia.org/wiki/Distributive\_lattice

Monads:
https://en.wikipedia.org/wiki/Monad\_(functional\_programming)

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

Tail Calls:
https://en.wikipedia.org/wiki/Tail\_call

On Recursion, Continuations and Trampolines:
https://eli.thegreenplace.net/2017/on-recursion-continuations-and-trampolines/
