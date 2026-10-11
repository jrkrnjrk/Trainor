class Priority:
    HIGH = 100
    NORMAL = 50
    LOW = 0

class Emitter:
    def __init__(self, *a, **k):
        self._handlers = {}

    def on(self, event, callback=None, priority=None):
        def deco(fn):
            self._handlers.setdefault(event, []).append(fn)
            return fn
        return deco if callback is None else deco(callback)

    def emit(self, event, *args, **kwargs):
        for fn in self._handlers.get(event, []):
            try:
                fn(*args, **kwargs)
            except Exception:
                pass
