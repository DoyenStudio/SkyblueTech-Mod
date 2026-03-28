# coding=utf-8
from weakref import ref

if 0:
    import typing

    T = typing.TypeVar("T", bound="typing.Callable")


def _is_py3():
    try:
        range(0)
        return True
    except NameError:
        return False


if _is_py3():
    _bound_attr = "__self__"
else:
    _bound_attr = "im_self"


def ref_method(method):
    # type: (T) -> typing.Callable[[], T | None]
    meth_name = method.__name__
    orig_instance = getattr(method, _bound_attr, None)
    if orig_instance is None:
        raise ValueError("method is not bound to an instance")
    instance_ref = ref(orig_instance)

    def caller():
        instance = instance_ref()
        if instance is None:
            return None
        else:
            return getattr(instance, meth_name)

    return caller


__all__ = ["ref_method"]
