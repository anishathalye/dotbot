class Singleton(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_singleton_instance"):
            cls._singleton_instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._singleton_instance

    def reset_instance(cls):
        if hasattr(cls, "_singleton_instance"):
            del cls._singleton_instance
