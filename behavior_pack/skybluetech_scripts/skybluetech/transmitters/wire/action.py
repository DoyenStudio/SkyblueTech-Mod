# coding=utf-8
from ..base import ActionModule
from .logic import logic_module

action_module = ActionModule(logic_module, enable_io_mode_settings=False)
