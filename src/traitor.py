

def impl_for(subject):
    if '_traitor_traits' not in subject.__dict__:
        subject._traitor_traits = {}
        subject._traitor_last_getattr = subject.__dict__.get('__getattr__', default_getattr)
        subject.__getattr__ = employ_traits

    def wrapper(impl):
        trait_name = impl.__name__
        trait = impl_for.traits[trait_name]

        impl._objects = []
        subject._traitor_traits[trait_name] = impl
        return trait

    return wrapper


impl_for.traits = {}


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
    trait_name = trait.__name__
    impl_for.traits[trait_name] = trait
    return trait

