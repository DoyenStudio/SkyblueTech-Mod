# coding=utf-8

"""
使用: `ImportModule("skybluetech_scripts.skybluetech.client.export")`
"""

additions = {}  # type: dict[str, str]


def AddAddition(mod_name, extension_name):
    # type: (str, str) -> None
    additions[mod_name] = extension_name
