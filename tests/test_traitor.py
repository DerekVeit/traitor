
from dataclasses import dataclass

from attrs import define
import pytest

from traitor import impl_for
from traitor import trait



def test_trait__by_call():
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    NewToUpper = trait(ToUpper)

    assert NewToUpper is ToUpper
    assert hasattr(ToUpper, 'to_upper')
    assert 'ToUpper' in impl_for.traits
    assert impl_for.traits['ToUpper'] is ToUpper



def test_trait():
    # act
    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    assert ToUpper.__name__ == 'ToUpper'
    assert hasattr(ToUpper, 'to_upper')
    assert 'ToUpper' in impl_for.traits
    assert impl_for.traits['ToUpper'] is ToUpper


def test_impl_for__adds_method():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl_for(Label)
    class ToUpper:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert hasattr(label, 'to_upper')


def test_impl_for__method_works():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl_for(Label)
    class ToUpper:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.to_upper() == 'LETTERS'


def test_impl_for__qual_method_works():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl_for(Label)
    class ToUpper:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.ToUpper.to_upper() == 'LETTERS'


def test_impl_for__ambiguous_method():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    @trait
    class Uppercase:
        def to_upper():
            "Return an uppercase value."

    @impl_for(Label)
    class ToUpper:
        def to_upper(self):
            return self.label.upper()

    @impl_for(Label)
    class Uppercase:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    with pytest.raises(AttributeError):
        label.to_upper()


def test_impl_for__disambiguous_method():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    @trait
    class Uppercase:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl_for(Label)
    class ToUpper:
        def to_upper(self):
            return self.label.upper()

    @impl_for(Label)
    class Uppercase:
        def to_upper(self):
            return 'Uppercase ' + self.label

    label = Label('letters')

    assert label.ToUpper.to_upper() == 'LETTERS'
    assert label.Uppercase.to_upper() == 'Uppercase letters'


@pytest.mark.parametrize('decorator', [define, dataclass])
def test_impl_for__special_subject(decorator):
    @decorator
    class Label:
        label: str

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl_for(Label)
    class ToUpper:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.to_upper() == 'LETTERS'


def test_impl_for__unknown_attr():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    @impl_for(Label)
    class ToUpper:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    with pytest.raises(AttributeError):
        label.nonexistent


def test_impl_for__getattr():
    class Label:
        def __init__(self, label):
            self.label = label
        def __getattr__(self, attr):
            if attr == 'original':
                return 'from the original'
            raise AttributeError('%r object has no attribute %r' %
                                 (type(obj).__name__, attr))

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl_for(Label)
    class ToUpper:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.to_upper() == 'LETTERS'
    assert label.original == 'from the original'


