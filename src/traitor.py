
import inspect

from zope.interface import Interface
from zope.interface.verify import verifyClass



def impl_for(subject):
    if '_traitor_traits' not in subject.__dict__:
        subject._traitor_traits = {}
        subject._traitor_last_getattr = subject.__dict__.get('__getattr__', default_getattr)
        subject.__getattr__ = employ_traits

    def wrapper(impl):
        trait_name = impl.__name__

        try:
            trait = inspect.stack()[1].frame.f_locals[trait_name]
        except KeyError:
            raise UnknownTrait('unknown trait {n!r}'.format(n=trait_name))

        if not getattr(trait, '_traitor_is_trait', False):
            raise UnknownTrait('{t!r} is not a trait'.format(t=trait))

        if issubclass(trait, Interface):
            verifyClass(trait, impl, tentative=True)

        impl._objects = []
        subject._traitor_traits[trait_name] = impl
        return trait

    return wrapper


class UnknownTrait(Exception):
    """
    impl_for was called on a class whose name does not match a declared trait.
    """


def default_getattr(obj, attr):
    raise AttributeError('%r object has no attribute %r' %
                         (type(obj).__name__, attr))


def employ_traits(obj, attr):
    if attr in obj._traitor_traits:
        impl = obj._traitor_traits[attr]
        impl._objects.append(obj)
        return obj

    impls = []

    for trait_name, impl in obj._traitor_traits.items():
        if attr in impl.__dict__:
            impls.append((trait_name, impl))
            if any(id(item) == id(obj) for item in impl._objects):
                impl._objects = [item for item in impl._objects if id(item) != id(obj)]
                impls = impls[-1:]
                break

    if len(impls) == 1:
        trait_name, impl = impls[0]
        def method(*args, **kwargs):
            return getattr(impl, attr)(obj, *args, **kwargs)
        return method
    elif len(impls) > 1:
        raise AttributeError('%r object has attribute %r for multiple traits' %
                             (type(obj).__name__, attr))

    return obj._traitor_last_getattr(attr)


def trait(trait):
    trait._traitor_is_trait = True
    return trait

