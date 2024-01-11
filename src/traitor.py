

def impl_for(subject):
    if '_traitor_traits' not in subject.__dict__:
        subject._traitor_traits = {}
        subject._traitor_last_getattr = subject.__dict__.get('__getattr__', default_getattr)
        subject.__getattr__ = employ_traits
    def wrapper(trait):
        trait._objects = []
        subject._traitor_traits[trait.__name__] = trait
        return impl_for.traits[trait.__name__]
    return wrapper

impl_for.traits = {}


def default_getattr(obj, attr):
    raise AttributeError('%r object has no attribute %r' %
                         (type(obj).__name__, attr))


def employ_traits(obj, attr):
    if attr in obj._traitor_traits:
        trait = obj._traitor_traits[attr]
        trait._objects.append(obj)
        return obj
    traits = []
    for trait_name, trait in obj._traitor_traits.items():
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
    return obj._traitor_last_getattr(attr)


def trait(cls):
    impl_for.traits[cls.__name__] = cls
    return cls

