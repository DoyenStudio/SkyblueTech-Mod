# coding=utf-8
#
class Iota(object):
    def __init__(self, start=0):
        # type: (int) -> None
        self.idx = self.start = start - 1

    def __call__(self, n=None):
        # type: (int | None) -> int
        if n is None:
            self.idx += 1
            return self.idx
        else:
            self.idx = self.start
            return self.idx

    def copy(self):
        return Iota(self.start)

__all__ = [
    'Iota'
]
