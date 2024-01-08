
from dataclasses import dataclass

def impl_for(subject):
    if '_traits' not in subject.__dict__:
        subject._traits = {}
        subject.__getattr__ = employ_traits
    def wrapper(trait):
        trait._objects = []
        subject._traits[trait.__name__] = trait
        return impl_for.traits[trait.__name__]
    return wrapper

impl_for.traits = {}


def employ_traits(obj, attr):
    if attr in obj._traits:
        trait = obj._traits[attr]
        trait._objects.append(obj)
        return obj
    traits = []
    for trait_name, trait in obj._traits.items():
        if attr in trait.__dict__:
            traits.append((trait_name, trait))
            if any(id(item) == id(obj) for item in trait._objects):
                trait._objects = [item for item in trait._objects if id(item) != id(obj)]
                traits = traits[-1:]
                break
    if len(traits) == 1:
        trait_name, trait = traits[0]
        def method(*args, **kwargs):
            return getattr(trait, attr)(obj, *args, **kwargs)
        return method
    elif len(traits) > 1:
        raise AttributeError('%r object has multiple traits defining attribute %r' %
                             (type(obj).__name__, attr))
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


@trait
class Reversal:
    def sorted(self):
        """
        returns a reversed sorted list
        """


@impl_for(Strings)
class Arrangement:
    def sorted(self):
        return sorted(self.strings)


@impl_for(Numbers)
class Arrangement:
    def sorted(self):
        return sorted(self.nums)



@impl_for(Numbers)
class Reversal:
    def sorted(self):
        return reversed(sorted(self.nums))



def main():
    lines = Strings('Ben Derek Carl Abe'.split())
    for line in lines.sorted():
        print(line)
    scores = Numbers([90, 84, 92, 87])
    for number in scores.Arrangement.sorted():
        print(number)
    for number in scores.sorted():
        print(number)

