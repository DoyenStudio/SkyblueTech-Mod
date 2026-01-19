# coding=utf-8
if 0:
    from typing import Union
    BASE_TYPE = type[str | int | float | bool] | None
    _KEY_TYPE = Union[BASE_TYPE, "TupleSchema", "FixedTupleSchema"]
    _VALUE_TYPE = BASE_TYPE | Union[
        "ListSchema",
        "DictSchema",
        "TupleSchema",
        "KeyDictSchema",
        "FixedTupleSchema"
    ]
    KEY_TYPE = _KEY_TYPE | tuple[_KEY_TYPE, ...]
    VALUE_TYPE = _VALUE_TYPE | tuple[_VALUE_TYPE, ...]
    SCHEMA_TYPE = _VALUE_TYPE | tuple["SCHEMA_TYPE", ...]

def check_generic(
    obj,
    schema, # type: SCHEMA_TYPE
):
    if isinstance(schema, tuple):
        for item in schema:
            if check_generic(obj, item):
                return True
        return False
    elif isinstance(
        schema,
        (
            DictSchema,
            ListSchema,
            TupleSchema,
            KeyDictSchema,
            FixedTupleSchema,
        )
    ):
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
        key_type, # type: KEY_TYPE
        value_type, # type: SCHEMA_TYPE
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
        value_type, # type: SCHEMA_TYPE
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
        value_type, # type: SCHEMA_TYPE
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


class FixedTupleSchema:
    def __init__(self, *tuple_value):
        # type: (SCHEMA_TYPE) -> None
        self.tuple_value = tuple_value

    def check(self, obj):
        if not isinstance(obj, tuple):
            return False
        if len(obj) != len(self.tuple_value):
            return False
        for schema, val in zip(self.tuple_value, obj):
            if not check_generic(val, schema):
                return False
        return True


class KeyDictSchema:
    def __init__(
        self,
        dict_value, # type: dict[str, SCHEMA_TYPE]
    ):
        self.dict_value = dict_value

    def check(self, obj):
        if not isinstance(obj, dict):
            return False
        if sorted(obj.keys()) != sorted(self.dict_value.keys()):
            return False
        for k, v in self.dict_value.items():
            if not check_generic(obj[k], v):
                return False
        return True
