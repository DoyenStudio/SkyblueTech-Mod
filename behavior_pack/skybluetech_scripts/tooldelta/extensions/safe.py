# coding=utf-8

def EnsureNBTSafe(
    arg,
    max_list_length=256,
    max_dict_length=256,
    max_string_length=1024,
    max_dict_key_length=256,
    max_bytes_length=4096,
    max_depth=16,
    _depth=0,
):
    if _depth > max_depth:
        return False
    if isinstance(arg, list):
        if len(arg) > max_list_length:
            return False
        for list_item in arg:
            if not EnsureNBTSafe(
                list_item,
                max_list_length=max_list_length,
                max_dict_length=max_dict_length,
                max_string_length=max_string_length,
                max_dict_key_length=max_dict_key_length,
                max_bytes_length=max_bytes_length,
                max_depth=max_depth,
                _depth=_depth + 1,
            ):
                return False
    elif isinstance(arg, dict):
        if len(arg) > max_dict_length:
            return False
        for k, v in arg.items():
            if len(k) > max_dict_key_length:
                return False
            if not EnsureNBTSafe(
                v,
                max_list_length=max_list_length,
                max_dict_length=max_dict_length,
                max_string_length=max_string_length,
                max_dict_key_length=max_dict_key_length,
                max_bytes_length=max_bytes_length,
                max_depth=max_depth,
                _depth=_depth + 1,
            ):
                return False
    elif isinstance(arg, str):
        if len(arg) > max_string_length:
            return False
    elif isinstance(arg, bytes):
        if len(arg) > max_bytes_length:
            return False
    elif not isinstance(arg, (int, float, bool)) and arg is not None:
        return False
    return True
