
from dataclasses import dataclass

def impl_for(subject):
    if '_traits' not in subject.__dict__:
        subject._traits = {}
        subject.__getattr__ = employ_traits
    def wrapper(trait):
        subject._traits[trait.__name__] = trait
        return impl_for.traits[trait.__name__]
    return wrapper

impl_for.traits = {}


def employ_traits(obj, attr):
    for trait in obj._traits.values():
        if attr in trait.__dict__:
            def method(*args, **kwargs):
                return getattr(trait, attr)(obj, *args, **kwargs)
            return method
    raise AttributeError('%r object has no attribute %r' %
                         (type(obj).__name__, attr))


def trait(cls):
    impl_for.traits[cls.__name__] = cls
    return cls


@dataclass
class Strings:
    strings: list[str]


@dataclass
class Numbers:
    nums: list[int]


@trait
class Arrangement:
    def sorted(self):
        """
        returns a sorted list
        """


@impl_for(Strings)
class Arrangement:
    def sorted(self):
        return sorted(self.strings)


@impl_for(Numbers)
class Arrangement:
    def sorted(self):
        return sorted(self.nums)



def main():
    lines = Strings('Ben Derek Carl Abe'.split())
    for line in lines.sorted():
        print(line)
    scores = Numbers([90, 84, 92, 87])
    for number in scores.sorted():
        print(number)

