# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode


class UnfinishedItemName(object):
    # GetItemHoverName 在模组刚加载时获取为空 需要 lazy load
    __slots__ = ("name",)

    def __init__(self, name):
        # type: (str) -> None
        self.name = name

    def __str__(self):
        # type: () -> str
        return cleaned_item_name(self.name)


def item_name_zh(item_id):
    # type: (str) -> str
    return GetItemHoverName(item_id) or item_id


def clean_name(name):
    # type: (str) -> str
    name_unicode = py2_unicode(name)
    if name_unicode.startswith(("§r", "§f")):  # noqa: FURB188
        name_unicode = name_unicode[2:]
    if name_unicode.endswith("§r"):  # noqa: FURB188
        name_unicode = name_unicode[:-2]
    return str(name_unicode)


def cleaned_item_name(item_id):
    # type: (str) -> str
    return clean_name(item_name_zh(item_id))

def finish_name(name):
    # type: (str | UnfinishedItemName) -> str
    if isinstance(name, UnfinishedItemName):
        name = name.name
    return cleaned_item_name(name)