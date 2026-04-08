# coding=utf-8
from .utils import color_convert


class Option(object):
    name = "opt"

    def __init__(self, params):
        # type: (dict) -> None
        self.params = params


class NewLine(object):
    name = "br"

    def __init__(self):
        pass


class Text(object):
    name = "text"

    def __init__(self, content, scale=None):
        # type: (str, float | None) -> None
        self.content = content
        self.scale = scale


class Style(object):
    name = "style"

    def __init__(self, color=None, scale=None):
        # type: (str | None, float | None) -> None
        self.color = color_convert(color) if color is not None else None
        self.scale = scale


class Image(object):
    name = "img"

    def __init__(self, path, x_scale=None, y_scale=None):
        # type: (str, float | None, float | None) -> None
        self.path = path
        self.x_scale = x_scale
        self.y_scale = y_scale


class ItemRender(object):
    name = "item"

    def __init__(self, item_id, item_aux, scale=None):
        # type: (str, int, float | None) -> None
        self.item_id = item_id
        self.item_aux = item_aux
        self.scale = scale


class HyperLink(object):
    name = "link"

    def __init__(self, text, id):
        # type: (str, str) -> None
        self.text = text
        self.id = id
