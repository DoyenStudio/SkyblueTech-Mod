# coding=utf-8
"机器类注册表; 不管理已加载的机器实例。"


# TYPE_CHECKING
if 0 > 1:
    import typing

    from ..basic import BaseMachine

    MT = typing.TypeVar("MT", bound=BaseMachine)
# TYPE_CHECKING END

registered_machines = {}  # type: dict[str, type[BaseMachine]]


def RegisterMachine(machine_cls):
    # type: (type[MT]) -> type[MT]
    """
    注册机器。所有机器类都必须使用此 `@RegisterMachine` 标注器标注。
    """
    if machine_cls.block_name:
        registered_machines[machine_cls.block_name] = machine_cls
    for interface_cls, extra_block_names in machine_cls._extra_block_names.items():
        for extra_block_name in extra_block_names:
            registered_machines[extra_block_name] = interface_cls
    return machine_cls


def GetMachineCls(block_name):
    # type: (str) -> type[BaseMachine]
    return registered_machines[block_name]


def TryGetMachineCls(block_name):
    # type: (str) -> type[BaseMachine] | None
    return registered_machines.get(block_name)
