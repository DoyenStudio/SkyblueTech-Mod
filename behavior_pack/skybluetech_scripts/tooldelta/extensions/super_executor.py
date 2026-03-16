class FuncMeta(type):
    """
    类方法覆盖执行类。

    使得类的 __metaclass__ = FuncMeta 后,
    再为类方法加上 @execute_super 装饰器
    就可以让最终子类在执行方法时按照继承顺序覆盖执行父类里的每一个同名方法 (也要 @execute_super 装饰)。
    """

    _ATTR_KEY = "_execute_super"

    def __new__(cls, name, bases, attrs):
        for attr_name, attr in attrs.items():
            if hasattr(attr, cls._ATTR_KEY):
                super_methods = cls._get_super_methods(attr_name, bases)

                def get_wrapper(_func, _methods):

                    def _func_wrapper(*args, **kwargs):
                        for meth in _methods:
                            if hasattr(meth, "_origin"):
                                meth._origin(*args, **kwargs)
                            else:
                                meth(*args, **kwargs)
                        _func(*args, **kwargs)

                    _func_wrapper._origin = _func
                    setattr(_func_wrapper, cls._ATTR_KEY, True)
                    return _func_wrapper

                attrs[attr_name] = get_wrapper(attr, super_methods[:])
        return super(FuncMeta, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def _get_super_methods(cls, name, bases):
        # type: (str, list) -> list
        methods = []
        for base_cls in bases:
            for meth in cls.__get_super_methods(base_cls, name):
                if meth not in methods:
                    methods.append(meth)
        return methods

    @classmethod
    def __get_super_methods(cls, current, name):
        # type: (type, str) -> list
        methods = []
        this_meth = getattr(current, name, None)
        if this_meth is None:
            return []
        if hasattr(this_meth, cls._ATTR_KEY):
            for base_cls in current.__bases__:
                meth = getattr(base_cls, name, None)
                if meth is not None:
                    if hasattr(meth, cls._ATTR_KEY):
                        for sub_meth in cls.__get_super_methods(base_cls, name):
                            if sub_meth not in methods:
                                methods.append(sub_meth)
                    if meth not in methods:
                        methods.append(meth)
        methods.append(this_meth)
        return methods

    @classmethod
    def execute_super(cls, func):
        func._execute_super = True
        return func
