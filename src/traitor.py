
import inspect

from zope.interface import Interface
from zope.interface.verify import verifyClass



def trait(trait):
    trait._traitor_is_trait = True
    return trait


def impl(impl):
    subject_name = impl.__name__

    for frame_info in inspect.stack()[1:]:
        if subject_name in frame_info.frame.f_locals:
            subject = frame_info.frame.f_locals[subject_name]
            break
    else:
        raise NameError('impl requires that {n!r} be previously defined'.format(n=subject_name))

    if '_traitor_traits' not in subject.__dict__:
        subject._traitor_traits = {}
        subject._traitor_last_getattr = subject.__dict__.get('__getattr__', _default_getattr)
        subject.__getattr__ = _traits_getattr

    impl._objects = []
    subject._traitor_traits[subject_name] = impl

    return subject


def _impl_of(trait):
    if not getattr(trait, '_traitor_is_trait', False):
        raise NotATrait('{t!r} is not a trait'.format(t=trait))

    def wrapper(impl):
        if issubclass(trait, Interface):
            verifyClass(trait, impl, tentative=True)

        subject_name = impl.__name__

        for frame_info in inspect.stack()[1:]:
            if subject_name in frame_info.frame.f_locals:
                subject = frame_info.frame.f_locals[subject_name]
                break
        else:
            raise NameError('impl requires that {n!r} be previously defined'.format(n=subject_name))

        if '_traitor_traits' not in subject.__dict__:
            subject._traitor_traits = {}
            subject._traitor_last_getattr = subject.__dict__.get('__getattr__', _default_getattr)
            subject.__getattr__ = _traits_getattr

        impl._objects = []
        subject._traitor_traits[trait.__name__] = impl
        return subject

    return wrapper


impl.of = _impl_of


def _default_getattr(obj, attr):
    raise AttributeError('%r object has no attribute %r' %
                         (type(obj).__name__, attr))


def _traits_getattr(obj, attr):
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


class NotATrait(Exception):
    """
    _impl_of was called with a class that is not a declared trait.
    """

