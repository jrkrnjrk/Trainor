class Enum(object):
    """Minimal enum stub compatible with holster.enum usage."""
    def __init__(self, *args, **kwargs):
        self._members = {}
        if args and isinstance(args[0], (list, tuple)):
            for i, name in enumerate(args[0]):
                self._members[name] = i
                setattr(self, name, i)
        for k, v in kwargs.items():
            self._members[k] = v
            setattr(self, k, v)

    def __iter__(self):
        return iter(self._members.items())

    def get(self, name, default=None):
        return self._members.get(name, default)
