
from dataclasses import dataclass

import pytest

from trait import impl_for
from trait import trait



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


@pytest.fixture
def lines():
    return Strings('Ben Derek Carl Abe'.split())


@pytest.fixture
def scores():
    return Numbers([90, 84, 92, 87])



def test_simple(lines):
    assert lines.sorted() == ['Abe', 'Ben', 'Carl', 'Derek']


def test_qualified(scores):
    assert scores.Arrangement.sorted() == [84, 87, 90, 92]


def test_unqualified(scores):
    with pytest.raises(AttributeError):
        scores.sorted()

