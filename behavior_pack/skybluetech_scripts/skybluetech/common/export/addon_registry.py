# coding=utf-8
# 附属模组命名空间注册表。

# 本模组不对任何附属模组做点名适配, 附属模组在自身加载完成后主动调用
# RegisterAddonNamespace 声明命名空间与分类中文名即可。注册后的命名空间会被本模组
# 视为自家内容, 并作为独立分类出现在 MiniJEI 物品页的分类下拉框中。

# 附属模组通过 ModSDK 的 ImportModule 取到本模块 (跨包 import 会触发机审告警):

#     registry = ImportModule(
#         "skybluetech_scripts.skybluetech.common.export.addon_registry"
#     )
#     registry.RegisterAddonNamespace("stasp", "太阳能板")

# 客户端与服务端各持有一份注册表, 需要哪一侧生效就在哪一侧注册。

MOD_NAMESPACE = "skybluetech"
MOD_DISPLAY_NAME = "蔚蓝科技"
ALL_DISPLAY_NAME = "全部"

_addon_namespaces = []  # type: list[str]
_addon_display_names = {}  # type: dict[str, str]


def RegisterAddonNamespace(namespace, display_name=None):
    # type: (str, str | None) -> None
    """注册附属模组的命名空间, 如 ("stasp", "太阳能板")。

    namespace 接受 "stasp" 或 "stasp:" 写法; display_name 为分类下拉框中的显示名,
    缺省时退化为命名空间本身。重复注册以最后一次的显示名为准。
    """
    namespace = (namespace or "").strip().rstrip(":")
    if not namespace:
        return
    if namespace not in _addon_display_names:
        _addon_namespaces.append(namespace)
    _addon_display_names[namespace] = display_name or namespace


def GetAddonNamespaces():
    # type: () -> list[str]
    return list(_addon_namespaces)


def GetCategoryOptions():
    # type: () -> list[tuple[str, str]]
    """分类下拉框选项: (显示名, 命名空间前缀), 前缀为空表示不过滤。顺序即显示顺序。"""
    options = [(ALL_DISPLAY_NAME, ""), (MOD_DISPLAY_NAME, MOD_NAMESPACE + ":")]
    for namespace in _addon_namespaces:
        options.append((_addon_display_names[namespace], namespace + ":"))
    return options


def GetNamespacePrefixes():
    # type: () -> tuple[str, ...]
    """本模组与全部已注册附属模组的命名空间前缀, 可直接用于 str.startswith。"""
    return tuple(prefix for _, prefix in GetCategoryOptions() if prefix)
