# coding=utf-8
from .utils import color_convert

class Option(object):
    def __init__(self, params):
        # type: (dict) -> None
        self.params = params

class NewLine(object):
    def __init__(self):
        pass


class Text(object):
    def __init__(self, content):
        # type: (str) -> None
        self.content = content


class Style(object):
    def __init__(self, color=None, scale=None):
        # type: (str | None, float | None) -> None
        self.color = color_convert(color) if color is not None else None
        self.scale = scale


class Image(object):
    def __init__(self, path, x_scale=None, y_scale=None):
        # type: (str, float | None, float | None) -> None
        self.path = path
        self.x_scale = x_scale
        self.y_scale = y_scale


class ItemRender(object):
    def __init__(self, item_id, item_aux, scale=None):
        # type: (str, int, float | None) -> None
        self.item_id = item_id
        self.item_aux = item_aux
        self.scale=scale


class HyperLink(object):

    def __init__(self, text, id):
        # type: (str, str) -> None
        self.text = text
        self.id = id

