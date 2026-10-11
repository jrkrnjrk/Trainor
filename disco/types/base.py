# Minimal disco compatibility stub for Railway (original library is unmaintained)
UNSET = object()
Unset = UNSET

class cached_property:
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, cls):
        if obj is None:
            return self
        val = self.f(obj)
        setattr(obj, self.f.__name__, val)
        return val

class Model:
    pass

class SlottedModel(Model):
    pass

class Field:
    def __init__(self, *a, **k):
        pass

class ListField(Field):
    pass

class DictField(Field):
    pass

def text(x):
    return str(x)

def snowflake(x):
    return int(x) if x is not None else None
