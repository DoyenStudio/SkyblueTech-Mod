if 0:
    from typing import Generic, TypeVar


class FakeGenericMeta(type):
    def __getitem__(cls, *args):
        return cls


class FakeGeneric(object):
    __metaclass__ = FakeGenericMeta


class FakeTypeVar(object):
    def __init__(self, *args, **kwargs):
        pass
