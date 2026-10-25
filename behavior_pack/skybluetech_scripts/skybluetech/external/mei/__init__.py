# coding=utf-8
"""
蔚蓝科技 → MoreEnoughItems (MEI) 的接入包。

MEI 是网易我的世界中国版的配方/物品浏览器（对标 JEI / EMI）。
本包把蔚蓝的机器配方注册进去，让玩家能在 MEI 里查粉碎机、合金炉这些配方。

**软依赖**：玩家没装 MEI 时 `CreateComponent` 给不出实例，整个包安静地什么都不做。
不需要在 netease_require.json 里声明 MEI，也不需要为它开可选分支包。

包内分工
--------
  bridge.py      全仓唯一的 MEI 接触点（组件 + ctx 门面）
  exports.py     蔚蓝侧数据的唯一接触点，只走正式导出（common.export.*）
  extension.py   MeiExtension 子类，三阶段生命周期
  runtime.py     需要继承 MEI 类型的类（基类是运行期取到的，只能在函数里定义）
  convert.py     蔚蓝配方 → MEI 配方，纯函数
  machines/      一台机器一个模块

接入时机
--------
挂在 `UiInitFinished` 上而不是客户端系统构造期：`CreateComponent` 要本地玩家 id，
构造期还没有。这一条是实机验过的（2026-09-03）——
跨 addon 的 `CreateComponent` **不需要** `modRequire`，只要调用点够晚。

另外要等**蔚蓝自己的客户端业务**加载完（`SkyblueTechClientLoaded`）：配方集合是那时建的。
实际顺序里它早于 `UiInitFinished`，这里仍按蔚蓝导出文档的要求先查 `IsClientLoaded()`。
"""
from skybluetech_scripts.tooldelta.events.client import UiInitFinishedEvent
from skybluetech_scripts.tooldelta.general import ClientInitCallback

from . import bridge, exports, extension

_EXTENSION_CLS = None
""" 扩展类只造一次。每次都新造一个类的话，MEI 那边会看成"另一个类来抢同一个 ID" """


def Setup():  # type: () -> bool
    """
    连 MEI 并注册扩展。**幂等**，可以每次进世界都调。

    返回是否注册成功；没装 MEI 返回 False，那不是错误。
    """
    global _EXTENSION_CLS

    if not exports.HasExports():
        # 本接入只按 next 框架的正式导出取数, 没有导出就明确说不兼容, 不退回读内部模块
        bridge.Error("当前蔚蓝科技没有正式导出接口(common.export), 跳过 MEI 接入")
        return False

    if not bridge.Connect():
        bridge.Info("未检测到 MoreEnoughItems, 跳过配方浏览器接入")
        return False

    if _EXTENSION_CLS is None:
        _EXTENSION_CLS = extension.Build()
    if _EXTENSION_CLS is None:
        return False

    # 注册时机不用操心: MEI 未就绪时会排队, 已就绪时立即装配
    if not bridge.Api.RegisterExtension(_EXTENSION_CLS):
        bridge.Error("MEI 拒绝了本扩展, 原因见它自己的日志")
        return False
    return True


@ClientInitCallback()
def _OnClientInit():
    """ 事件监听要在客户端系统就绪后挂，这是 ToolDelta 的惯例 """

    @UiInitFinishedEvent.Listen()
    def _OnUiInitFinished(_event):
        if not exports.HasExports() or exports.IsClientLoaded():
            Setup()     # 没有导出时 Setup 自己会报不兼容
        else:
            exports.ListenClientLoaded(Setup)
