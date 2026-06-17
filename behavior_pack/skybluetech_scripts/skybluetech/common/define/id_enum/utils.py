# coding=utf-8
class _SimpleEnumMeta(type):
    _keywords = {"all", "all_sub", "add_extras"}
    _children_classes = {}  # type: dict[type[SimpleEnum], set[type[SimpleEnum]]]

    def __init__(self, name, bases, attrs):
        super(_SimpleEnumMeta, self).__init__(name, bases, attrs)
        if name == "SimpleEnum":
            return
        if issubclass(self, SimpleEnum):
            for base in bases:
                if issubclass(base, SimpleEnum):
                    self._children_classes.setdefault(base, set()).add(self)
            own_enum_values = set(
                v
                for k, v in attrs.items()
                if k not in _SimpleEnumMeta._keywords and k[0] != "_"
            )  # type: set[str]
            enum_values = set(own_enum_values)
            for base in self.__bases__:
                if issubclass(base, SimpleEnum):
                    enum_values.update(base.all())
            self._all_enums.setdefault(self, set()).update(enum_values)
            self._update_sub_enums(own_enum_values)


class SimpleEnum(object):
    __metaclass__ = _SimpleEnumMeta
    """
    简易字符串枚举类。
    """
    _all_enums = {}  # type: dict[type[SimpleEnum], set[str]]
    _all_sub_enums = {}  # type: dict[type[SimpleEnum], set[str]]

    @classmethod
    def all(cls):
        """
        获取本枚举类下所有枚举值。
        """
        return cls._all_enums.setdefault(cls, set())

    @classmethod
    def all_sub(cls):
        """
        获取本枚举类下所有子枚举值, 包括本枚举类子类的枚举值。
        """
        return cls._all_sub_enums.setdefault(cls, set())

    @classmethod
    def add_extras(cls, extras):
        # type: (set[str]) -> None
        """
        添加额外的枚举值。
        """
        cls.all().update(extras)
        cls._update_sub_enums(extras)
        cls._add_enums_from_parent(extras)

    @classmethod
    def _update_sub_enums(cls, enum_values, _walked=None):
        # type: (set[str], set[type[SimpleEnum]] | None) -> None
        """
        添加来自子类的枚举值。
        """
        if _walked is None:
            _walked = set()
        cls.all_sub().update(enum_values)
        for parent in cls.__bases__:
            if issubclass(parent, SimpleEnum):
                if parent in _walked:
                    continue
                _walked.add(parent)
                parent._update_sub_enums(enum_values, _walked)

    @classmethod
    def _add_enums_from_parent(cls, enum_values, _walked=None):
        # type: (set[str], set[type[SimpleEnum]] | None) -> None
        """
        添加来自父类的枚举值。
        """
        if _walked is None:
            _walked = set()
        cls.all().update(enum_values)
        for child in _SimpleEnumMeta._children_classes.get(cls, set()):
            if child in _walked:
                continue
            _walked.add(child)
            child._add_enums_from_parent(enum_values, _walked)
