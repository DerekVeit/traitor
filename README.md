# traitor - Imitation of Rust's trait and impl

The Python language provides the common abstraction of a class, which combines a data structure and behavior related to it.  The Rust language takes a different approach, with a "struct" for a data structure and an "impl" for behavior.  Another Rust feature, a "trait", defines only the interface of a behavior, which might be useful for a variety of structs but implemented differently for each one.  The implementation of a trait for a struct is an impl.

This library allows using this approach in Python.

## Example:

```python
from traitor import trait, impl_for

class Foo:
    def __init__(self, bar):
        self.bar = bar

@trait
class Bazziness:
    def baz():
        "Give something bazzy."

@impl_for(Foo)
class Bazziness:
    def baz(self):
        return f'BAZ {self.bar} BAZ'

some_foo = Foo('ok')

assert some_foo.bar() == 'ok'
assert some_foo.baz() == 'BAZ ok BAZ'
```

## Terms

* **data class** - a class for data
  
  * Would be a struct in Rust.
  * Normally a class without public methods but can be any ordinary class.
  * Does not need decoration, but `@dataclass` or [attrs](https://www.attrs.org) `@define` would be appropriate.

* **trait** - a class defining an interface
  
  * Decorated with `@trait`.
  * Defines abstract behavior.
  * Can be defined as a `zope.interface.Interface` or similarly.

* **impl** - a class defining the implementation of a trait for a data class
  
  * Decorated with `@impl_for`.
  * Defines actual behavior.
  * If the trait is a `zope.interface.Interface`, the impl will be validated against it.

## Multiple traits

Multiple traits can be implemented for a data class.

In case a method name is part of more than one trait implemented for a data class, a method call can be qualified by the trait name:

```python
from attrs import define
from traitor import trait, impl_for

# The data class:

@define
class Phrase:
    text: str

# Two traits, both having a "sorted" method:

@trait
class WordSorting:
    def sorted():
        "Sort the words."
    def first():
        "First sorted word."

@trait
class CharSorting:
    def sorted():
        "Sort the characters."

# Both traits implemented for Phrase:

@impl_for(Phrase)
class WordSorting:
    def sorted(self):
        return ' '.join(self._sorted())
    def first(self):
        return self._sorted()[0]
    def _sorted(self):
        return sorted(self.text.split())

@impl_for(Phrase)
class CharSorting:
    def sorted(self):
        return ''.join(sorted(self.text))

# A Phrase object:

title = Phrase('The Rust Programming Language')

assert title.first() == 'Language'

# Calling title.sorted() would raise an AttributeError for the ambiguity:
#     AttributeError: 'Phrase' object has attribute 'sorted' for multiple traits
# But qualifying it with a trait works:

assert title.WordSorting.sorted() == 'Language Programming Rust The'
assert title.CharSorting.sorted() == '   LPRTaaaeegggghimmnnorrstuu'
```

## How It Works

The `@trait` decorator

- Adds a `_traitor_is_trait` attribute to the decorated class, which the `@impl_for` decorator will look for.

The `@impl_for` decorator

- Adds these attributes to the data class:
  
  - `_traitor_traits` : a dict containing the impl assigned for each trait implemented for the data class.
  
  - `_traitor_last_getattr` : the existing `__getattr__` method if the data class has one or otherwise  a  method that just raises `AttributeError`.
  
  - `__getattr__` : a method for accessing impl attributes, which, if it finds nothing, calls `_traitor_last_getattr`.

- Finds the trait class having the name of the decorated class and, if it is a `zope.interface.Interface`, validates the impl (the decorated class) against it.

- Returns the *trait* class, so that the class definition of the impl, which has the same name, does not replace it in the current scope.
