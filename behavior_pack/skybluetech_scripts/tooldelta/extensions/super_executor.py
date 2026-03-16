class SuperExecutorMeta(type):
    """
    类方法覆盖执行类。

    使得类的 __metaclass__ = FuncMeta 后,
    再为类方法加上 @execute_super 装饰器
    就可以让最终子类在执行方法时按照继承顺序覆盖执行父类里的每一个同名方法 (也要 @execute_super 装饰)。
    """

    _ATTR_KEY = "_execute_super"
    _ATTR_BLACKLIST_KEY = "_execute_super_blacklist"

    def __new__(cls, name, bases, attrs):
        for attr_name, attr in attrs.items():
            if hasattr(attr, cls._ATTR_KEY):
                cls_blacklist = getattr(attr, cls._ATTR_BLACKLIST_KEY, set())
                super_methods = cls._get_super_methods(attr_name, bases, cls_blacklist)

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
        return super(SuperExecutorMeta, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def _get_super_methods(cls, name, bases, cls_blacklist):
        # type: (str, list, set[type]) -> list
        methods = []
        for base_cls in bases:
            for meth in cls.__get_super_methods(base_cls, name, cls_blacklist):
                if meth not in methods:
                    methods.append(meth)
        return methods

    @classmethod
    def __get_super_methods(cls, current, name, cls_blacklist):
        # type: (type, str, set[type]) -> list
        methods = []
        this_meth = getattr(current, name, None)
        if this_meth is None:
            return []
        if hasattr(this_meth, cls._ATTR_KEY):
            for base_cls in current.__bases__:
                meth = getattr(base_cls, name, None)
                if meth is not None:
                    if hasattr(meth, cls._ATTR_KEY):
                        sub_meths = cls.__get_super_methods(
                            base_cls, name, cls_blacklist
                        )
                        for sub_meth in sub_meths:
                            if sub_meth not in methods:
                                methods.append(sub_meth)
                    if meth not in methods:
                        methods.append(meth)
        if current not in cls_blacklist:
            methods.append(this_meth)
        return methods

    @classmethod
    def execute_super(cls, func):
        func._execute_super = True
        func._execute_super_blacklist = set()
        return func

    @classmethod
    def execute_super_with_blacklist(cls, *blacklist_args):
        def wrapper(func):
            func._execute_super = True
            func._execute_super_blacklist = set(blacklist_args)
            return func

        return wrapper
