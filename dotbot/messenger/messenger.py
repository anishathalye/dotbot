import sys
from ..util.singleton import Singleton
from ..util.compat import with_metaclass
from .color import Color
from .level import Level

class Messenger(with_metaclass(Singleton, object)):
    def __init__(self, level = Level.LOWINFO):
        self.set_level(level)

    def set_level(self, level):
        self._level = level

    def log(self, level, message):
        if (level >= self._level):
            print('%s%s%s' % (self._color(level), message, self._reset()))

    def debug(self, message):
        self.log(Level.DEBUG, message)

    def lowinfo(self, message):
        self.log(Level.LOWINFO, message)

    def info(self, message):
        self.log(Level.INFO, message)

    def warning(self, message):
        self.log(Level.WARNING, message)

    def error(self, message):
        self.log(Level.ERROR, message)

    def _color(self, level):
        '''
        Get a color (terminal escape sequence) according to a level.
        '''
        if not sys.stdout.isatty():
            return ''
        elif level < Level.DEBUG:
            return ''
        elif Level.DEBUG <= level < Level.LOWINFO:
            return Color.YELLOW
        elif Level.LOWINFO <= level < Level.INFO:
            return Color.BLUE
        elif Level.INFO <= level < Level.WARNING:
            return Color.GREEN
        elif Level.WARNING <= level < Level.ERROR:
            return Color.MAGENTA
        elif Level.ERROR <= level:
            return Color.RED

    def _reset(self):
        '''
        Get a reset color (terminal escape sequence).
        '''
        if not sys.stdout.isatty():
            return ''
        else:
            return Color.RESET
