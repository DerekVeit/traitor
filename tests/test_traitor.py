
from dataclasses import dataclass

from attrs import define
import pytest
from zope.interface import Interface
from zope.interface import Invalid

from traitor import impl_for
from traitor import trait
from traitor import UnknownTrait



def test_trait__by_call():
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    NewToUpper = trait(ToUpper)

    assert NewToUpper is ToUpper
    assert hasattr(ToUpper, 'to_upper')
    assert hasattr(ToUpper, '_traitor_is_trait')



def test_trait():
    # act
    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    assert ToUpper.__name__ == 'ToUpper'
    assert hasattr(ToUpper, 'to_upper')
    assert hasattr(ToUpper, '_traitor_is_trait')


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


def test_impl_for__unknown_trait():
    class Label:
        def __init__(self, label):
            self.label = label

    with pytest.raises(UnknownTrait):
        @impl_for(Label)
        class ToUpper:
            def to_upper(self):
                return self.label.upper()


def test_impl_for__not_a_trait():
    class Label:
        def __init__(self, label):
            self.label = label

    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    with pytest.raises(UnknownTrait):
        @impl_for(Label)
        class ToUpper:
            def to_upper(self):
                return self.label.upper()


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
                                 (type(self).__name__, attr))

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
    with pytest.raises(AttributeError):
        label.nonexistent


def test_impl_for__interface():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper(Interface):
        def to_upper():
            "Return an uppercase value."

    # act
    @impl_for(Label)
    class ToUpper:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.to_upper() == 'LETTERS'


def test_impl_for__interface_reject():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper(Interface):
        def to_upper():
            "Return an uppercase value."

    with pytest.raises(Invalid):
        @impl_for(Label)
        class ToUpper:
            def to_lower(self):
                return self.label.lower()


def test_impl_for__other_scope():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    def inner():
        @impl_for(Label)
        class ToUpper:
            def to_upper(self):
                return self.label.upper()

        label = Label('letters')

        return label.ToUpper.to_upper()

    result = inner()

    assert result == 'LETTERS'

