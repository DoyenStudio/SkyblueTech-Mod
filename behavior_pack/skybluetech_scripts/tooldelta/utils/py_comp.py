# coding=utf-8

try:
    xrange  # type: ignore
except NameError:
    xrange = range

try:
    unicode  # type: ignore
except NameError:
    unicode = str
