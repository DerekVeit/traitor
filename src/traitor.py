
import inspect

from zope.interface import Interface
from zope.interface.verify import verifyClass



def trait(trait):
    trait._traitor_is_trait = True
    return trait


def impl(impl):
    return _impl(impl, frame=2)


def _impl(impl, frame=1, trait=None):
    subject_name = impl.__name__

    if trait is not None:
        if issubclass(trait, Interface):
            verifyClass(trait, impl, tentative=True)
        trait_name = trait.__name__
    else:
        trait_name = subject_name

    for frame_info in inspect.stack()[frame:]:
        if subject_name in frame_info.frame.f_locals:
            subject = frame_info.frame.f_locals[subject_name]
            break
    else:
        raise NameError('impl requires that {n!r} be previously defined'.format(n=subject_name))

    if '_traitor_traits' not in subject.__dict__:
        subject._traitor_traits = {}
        subject._traitor_last_getattr = subject.__dict__.get('__getattr__', _default_getattr)
        subject.__getattr__ = _traits_getattr

    impl.__init__ = _impl_init
    impl.__getattr__ = _impl_getattr

    subject._traitor_traits[trait_name] = impl

    return subject


def _impl_of(trait):
    if not getattr(trait, '_traitor_is_trait', False):
        raise NotATrait('{t!r} is not a trait'.format(t=trait))

    def wrapper(impl):
        return _impl(impl, trait=trait)

    return wrapper


impl.of = _impl_of


def _default_getattr(obj, attr):
    raise AttributeError('%r object has no attribute %r' %
                         (type(obj).__name__, attr))


def _traits_getattr(obj, attr):
    if attr in obj._traitor_traits:
        impl = obj._traitor_traits[attr]
        return impl(obj, attr)

    impls = []

    for trait_name, impl in obj._traitor_traits.items():
        if attr in impl.__dict__:
            impls.append((trait_name, impl))

    if len(impls) == 1:
        trait_name, impl = impls[0]
        value = getattr(impl, attr)
        if callable(value):
            def method(*args, **kwargs):
                return value(obj, *args, **kwargs)
            return method
        return value
    elif len(impls) > 1:
        raise AttributeError('%r object has attribute %r for multiple traits' %
                             (type(obj).__name__, attr))

    return obj._traitor_last_getattr(attr)


def _impl_init(obj, original, trait_name):
    obj._original = original
    obj._trait_name = trait_name


def _impl_getattr(obj, attr):
    return getattr(obj._original, attr)


class NotATrait(Exception):
    """
    _impl_of was called with a class that is not a declared trait.
    """

