from enum import Enum
from typing import Any


class Level(Enum):
    NOTSET = 0
    DEBUG = 10
    LOWINFO = 15
    INFO = 20
    WARNING = 30
    ERROR = 40

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.value >= other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.value == other.value
