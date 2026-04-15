# coding=utf-8


class SimpleEnum(object):
    _all = None
    _keywords = {"all"}

    @classmethod
    def all(cls):
        if cls._all is None:
            cls._all = {
                getattr(cls, name)
                for name in dir(cls)
                if name[0] != "_" and name not in cls._keywords
            }
        return cls._all
