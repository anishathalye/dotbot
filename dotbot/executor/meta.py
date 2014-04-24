from . import Executor

class Meta(Executor):
    '''
    Dummy handler for metadata support
    '''

    _directive = 'meta'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Header cannot handle directive %s' % directive)
        return True
