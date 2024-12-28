from typing import Any


class Singleton(type):
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if not hasattr(cls, "_singleton_instance"):
            cls._singleton_instance = super().__call__(*args, **kwargs)
        return cls._singleton_instance

    def reset_instance(cls) -> None:
        if hasattr(cls, "_singleton_instance"):
            del cls._singleton_instance
