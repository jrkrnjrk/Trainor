class Bot:
    pass

class CommandLevels:
    ADMIN = 100
    MOD = 50
    TRUSTED = 10
    EVERYONE = 0

class Plugin:
    @classmethod
    def command(cls, *args, **kwargs):
        """Stub decorator so @Plugin.command(...) doesn't crash on import."""
        def decorator(fn):
            return fn
        return decorator

    @classmethod
    def listen(cls, *args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

    @classmethod
    def with_config(cls, *args, **kwargs):
        def decorator(fn):
            return fn
        return decorator
