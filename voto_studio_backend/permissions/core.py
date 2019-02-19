READ_PERMISSION = 'read'
WRITE_PERMISSION = 'write'
DELETE_PERMISSION = 'delete'
RELATE_PERMISSION = 'relate'
COMMIT_PERMISSION = 'commit'
REVERT_PERMISSION = 'revert'


PERMISSIONS_HIERARCHY = [
    'commit',
    'write',
    'read',
]


class Permission:
    def __init__(self, *args):
        self.level = args[0]

    def __eq__(self, other):
        return self.level == other.level

    def __lt__(self, other):
        return PERMISSIONS_HIERARCHY.index(self.level) > \
               PERMISSIONS_HIERARCHY.index(other.level)

    def __gt__(self, other):
        return not self.__lt__(other)

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __add__(self, other):
        if self > other:
            return self
        else:
            return other

    def __sub__(self, other):
        if self < other:
            return self
        else:
            return other

    def __str__(self):
        return self.level

    def __call__(self, *args, **kwargs):
        return self.level
