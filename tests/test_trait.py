
from trait import impl_for
from trait import trait

from dataclasses import dataclass


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


main()
