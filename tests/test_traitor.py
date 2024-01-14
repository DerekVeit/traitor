
from dataclasses import dataclass

from attrs import define
import pytest
from zope.interface import Interface
from zope.interface import Invalid

from traitor import impl
from traitor import trait
from traitor import NotATrait



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


def test_impl_of__adds_method():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert hasattr(label, 'to_upper')


def test_impl_of__method_works():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.to_upper() == 'LETTERS'


def test_impl_of__qual_method_works():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.ToUpper.to_upper() == 'LETTERS'


def test_impl_of__ambiguous_method():
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

    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()

    @impl.of(Uppercase)
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    with pytest.raises(AttributeError):
        label.to_upper()


def test_impl_of__disambiguous_method():
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
    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()

    @impl.of(Uppercase)
    class Label:
        def to_upper(self):
            return 'Uppercase ' + self.label

    label = Label('letters')

    assert label.ToUpper.to_upper() == 'LETTERS'
    assert label.Uppercase.to_upper() == 'Uppercase letters'


@pytest.mark.parametrize('decorator', [define, dataclass])
def test_impl_of__special_subject(decorator):
    @decorator
    class Label:
        label: str

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.to_upper() == 'LETTERS'


def test_impl_of__unknown_trait():
    class Label:
        def __init__(self, label):
            self.label = label

    with pytest.raises(NameError):
        @impl.of(ToUpper)
        class Label:
            def to_upper(self):
                return self.label.upper()


def test_impl_of__not_a_trait():
    class Label:
        def __init__(self, label):
            self.label = label

    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    with pytest.raises(NotATrait):
        @impl.of(ToUpper)
        class Label:
            def to_upper(self):
                return self.label.upper()


def test_impl_of__unknown_attr():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    with pytest.raises(AttributeError):
        label.nonexistent


def test_impl_of__getattr():
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
    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.to_upper() == 'LETTERS'
    assert label.original == 'from the original'
    with pytest.raises(AttributeError):
        label.nonexistent


def test_impl_of__interface():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper(Interface):
        def to_upper():
            "Return an uppercase value."

    # act
    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.to_upper() == 'LETTERS'


def test_impl_of__interface_reject():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper(Interface):
        def to_upper():
            "Return an uppercase value."

    with pytest.raises(Invalid):
        @impl.of(ToUpper)
        class Label:
            def to_lower(self):
                return self.label.lower()


def test_impl_of__other_scope():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    def inner():
        @impl.of(ToUpper)
        class Label:
            def to_upper(self):
                return self.label.upper()

        label = Label('letters')

        return label.ToUpper.to_upper()

    result = inner()

    assert result == 'LETTERS'


def test_impl__adds_method():
    class Label:
        def __init__(self, label):
            self.label = label

    # act
    @impl
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert hasattr(label, 'to_upper')


def test_impl__method_works():
    class Label:
        def __init__(self, label):
            self.label = label

    # act
    @impl
    class Label:
        def to_upper(self):
            return self.label.upper()

    label = Label('letters')

    assert label.to_upper() == 'LETTERS'


def test_impl__and_impl_of():
    class Label:
        def __init__(self, label):
            self.label = label

    @trait
    class ToUpper:
        def to_upper():
            "Return an uppercase value."

    # act
    @impl
    class Label:
        def abbreviate(self):
            return ''.join(word[0] + '.' for word in self.label.split())
        def to_upper(self):
            return self.label + ' -> upper'

    @impl.of(ToUpper)
    class Label:
        def to_upper(self):
            return self.label.upper()
        def to_upper_with_emphasis(self):
            return self.label.upper() + '!'

    label = Label('letters')

    assert label.abbreviate() == 'l.'
    assert label.to_upper_with_emphasis() == 'LETTERS!'
    assert label.ToUpper.to_upper() == 'LETTERS'
    assert label.Label.to_upper() == 'letters -> upper'
    with pytest.raises(AttributeError):
        label.to_upper

