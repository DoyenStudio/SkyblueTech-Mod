# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import CustomCommandTriggerServerEvent


def generate_simple_arg_mapping(arg_list):
    # type: (list) -> dict
    res = {}
    for arg in arg_list:
        res[arg["name"]] = arg["value"]
    return res
