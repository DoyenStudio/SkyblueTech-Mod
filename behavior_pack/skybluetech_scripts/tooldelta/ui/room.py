# coding=utf-8

def _regist_content(attr):
    # type: (type) -> str
    globals()[attr.__name__] = attr
    attr.__module__ = _regist_content.__module__
    return attr.__module__ + "." + attr.__name__
