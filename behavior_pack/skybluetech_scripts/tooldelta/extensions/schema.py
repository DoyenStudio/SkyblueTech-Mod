# coding=utf-8
if 0:
    from typing import Union
    BASE_TYPE = type[str | int | float | bool | None]
    _KEY_TYPE = Union[BASE_TYPE, "TupleSchema"]
    _VALUE_TYPE = BASE_TYPE | Union["ListSchema", "DictSchema", "TupleSchema"]
    KEY_TYPE = _KEY_TYPE | tuple[_KEY_TYPE, ...]
    VALUE_TYPE = _VALUE_TYPE | tuple[_VALUE_TYPE, ...]
    SCHEMA_TYPE = BASE_TYPE | Union["ListSchema", "DictSchema", "TupleSchema"] | tuple["SCHEMA_TYPE", ...]

def check_generic(
    obj,
    schema, # type: SCHEMA_TYPE
):
    if isinstance(schema, tuple):
        for item in schema:
            if not check_generic(obj, item):
                return False
        return True
    elif isinstance(schema, (DictSchema, ListSchema, TupleSchema)):
        return schema.check(obj)
    elif isinstance(schema, type):
        if schema is int:
            return isinstance(obj, int)
        elif schema is float:
            return isinstance(obj, float)
        elif schema is str:
            return isinstance(obj, str)
        elif schema is bool:
            return isinstance(obj, bool)
    elif schema is None:
        return obj is None
    else:
        raise ValueError("Invalid schema type {}".format(schema))


class DictSchema:
    def __init__(
        self,
        key_type, # type: type[str | int | float | bool | None] | TupleSchema
        value_type, # type: type[str | int | float | bool | None] | ListSchema | DictSchema | TupleSchema
    ):
        self.key_type = key_type
        self.value_type = value_type

    def check(self, obj):
        if not isinstance(obj, dict):
            return False
        for k, v in obj.items():
            if not check_generic(k, self.key_type) or not check_generic(v, self.value_type):
                return False
        return True


class ListSchema:
    def __init__(
        self,
        value_type, # type: type[str | int | float | bool | None] | ListSchema | DictSchema | TupleSchema
        min_length=None, # type: int | None
        max_length=None, # type: int | None
    ):
        self.value_type = value_type
        self.min_length = min_length
        self.max_length = max_length

    def check(self, obj):
        if not isinstance(obj, list):
            return False
        if self.min_length is not None and len(obj) < self.min_length:
            return False
        if self.max_length is not None and len(obj) > self.max_length:
            return False
        for v in obj:
            if not check_generic(v, self.value_type):
                return False
        return True


class TupleSchema:
    def __init__(
        self,
        value_type, # type: type[str | int | float | bool | None] | ListSchema | DictSchema | TupleSchema
        min_length=None, # type: int | None
        max_length=None, # type: int | None
    ):
        self.value_type = value_type
        self.min_length = min_length
        self.max_length = max_length

    def check(self, obj):
        if not isinstance(obj, list):
            return False
        if self.min_length is not None and len(obj) < self.min_length:
            return False
        if self.max_length is not None and len(obj) > self.max_length:
            return False
        for v in obj:
            if not check_generic(v, self.value_type):
                return False
        return True
