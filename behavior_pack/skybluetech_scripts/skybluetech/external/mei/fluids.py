# coding=utf-8
"""
流体条目：`Stack.KIND == "fluid"` 的那一半。

**为什么流体不用另造物品**：`skybluetech:raw_oil` 是 `base_block: liquid` +
`category: none` 的方块，落进 `GetLoadItems(True) - GetLoadItems(False)` 的隐藏表，
客户端照常注册 ⇒ **它本来就是 MEI 里的一个 Item**（2026-09-04 实机确认）。
所以索引 / 查询 / 书签 / 键一处都不用改，要分发的只有**渲染**
——这正是 MEI `SlotPanelRegistry` 的用途。

**为什么 `FluidPanel` 继承 `ItemPanel` 而不是从零写一个**：
MEI 的槽位前缀绑定集是**按 `mei_common.item_panel` 的控件结构写死的**
（`.item.renderer.visible` / `.item.label.text` / `.overlay.btn.hover_text` …
共 9 条，见 `utils/utilities.py::GetItemPanelBindingConfigs`）。
换句话说 —— **回调之所以会被调用，是因为 JSON 里那条 `#<prefix>.visible` 绑定**。
自建一个没有这些绑定的控件，`render_slot` 永远不会被调到，且**零报错**。
⇒ 流体格 = `@mei_common.item_panel` + 一个 `fluid/img` 子控件，
点击查用途、hover、可见性全部白送，我们只多画一条液面。
"""
from . import bridge, exports

KIND = "fluid"
""" 注册给 MEI 的条目种类。与 `Stack.KIND` 同一个字符串 """

NEWLINE = "\n"
""" hover 文本的换行。单独取个名是为了不在多行字符串拼接里写转义 """

FRAME_SIZE = 16
""" 流体贴图一帧的边长（像素），同蔚蓝 `client/ui/machinery/utils.py` 的 FLUID_FRAME_SIZE；导出没给 """

DEFAULT_TEXTURE = ("textures/fluid/basic_fluid", (255, 255, 255), 255)
""" 取不到贴图时的兜底，与蔚蓝 GetFluidTexture 的默认值一致 """

_STACK = [None]
_PANEL = [None]
""" 类只造一次（理由同 runtime.py）。

    **堆与面板分两个工厂而不是一个 `Build()`**：
    数据转换（`convert._typed`）只需要 `FluidStack`，合成一个工厂会把
    `ItemPanel` —— 一整条 UI 依赖 —— 拖进纯数据路径里。
    那正是 MEI 自己在「包门面急加载把引擎拖进纯逻辑层」上栽过三次的那类债
    （CLAUDE.md 「待偿还」节），不重蹈。 """


def StackCls():  # type: () -> type
    """ `FluidStack`。**不碰 UI** —— 数据转换路径只用这一个 """
    if _STACK[0] is None:
        _STACK[0] = _BuildStack()
    return _STACK[0]


def PanelCls():  # type: () -> type
    """ `FluidPanel`。只有注册面板那一处用得到 """
    if _PANEL[0] is None:
        _PANEL[0] = _BuildPanel()
    return _PANEL[0]


# 纯函数部分（模块级，不碰 MEI 类型）
# ======================================================================================================================
def FormatVolume(volume):  # type: (float) -> str
    """ 体积文字。与蔚蓝自己的 `FormatFluidVolume` 同规则，别让两处显示对不上 """
    volume = float(volume or 0)
    if volume >= 10000:
        return "%.2fB" % (volume / 1000.0)
    return "%.0fmB" % volume


def Texture(fluid_id):  # type: (str) -> tuple
    """ (贴图路径, (r,g,b), alpha 0~255)。**表在蔚蓝这边，MEI 一个流体 id 都不认识** """
    try:
        texture = exports.Fluids().GetFluidTexture(fluid_id)
        return texture.basic_texture.texture_path, tuple(texture.rgb), int(texture.alpha)
    except Exception:  # noqa  取不到就用默认贴图, 不该因为一格流体炸掉整页
        return DEFAULT_TEXTURE


def IsGas(fluid_id):  # type: (str) -> bool
    """ 气体的液面**从上往下**长（蔚蓝 FluidDisplayer 的约定） """
    try:
        # all_sub 而不是 all: 后者不含子类的值, 压缩空气这类 CommonGas 会被当成液体
        return fluid_id in exports.Fluids().Gas.all_sub()
    except Exception:  # noqa  拿不到气体表就当液体, 只是方向不同, 不致命
        return False


# 运行期类（要 MEI 基类，只能在函数里定义）
# ======================================================================================================================
def _BuildStack():  # type: () -> type
    ItemStack = bridge.Types.ItemStack

    class FluidStack(ItemStack):
        """
        一堆流体。**除了 KIND 什么都不改** —— 身份、序列化、相等判断
        全部沿用 `ItemStack`，所以加这个类不会漂移 `Recipe.Id`。

        `Count` 就是体积（mB）。蔚蓝的体积全是整数（50 / 144 / 2000 …），
        而 `FormatVolume` 在 <10000 时本来就是 `"%.0f mB"` ⇒ 取整无显示损失。
        """

        __slots__ = ()
        """ 不加实例属性；漏写会让子类多出一个 __dict__ """

        KIND = "fluid"
        """ 必须与模块级的 KIND 一致 —— 注册面板与打标记是同一个字符串。
            这里不写 `KIND = KIND`: py2 的 class 体看不见外层函数的局部变量,
            那行能跑是因为恰好落到了模块全局, 太绕 """

    return FluidStack


def _BuildPanel():  # type: () -> type
    ItemPanel = bridge.UI.Controls.ItemPanel

    class FluidPanel(ItemPanel):
        """
        流体槽。布局见 `ui/mei_recipes/common.json` 的 `fluid_slot`。

        与 `ItemPanel` 的差别只有三条：
          · 不画物品图标（`ItemRendererVisible = False`）；
          · `/item/label` 改写体积而不是堆叠数 —— **复用现成绑定**，不新增；
          · 多画一条按体积撑高的液面 `/fluid/img`（直推控件，无绑定）。
        """

        FLUID_IMG_PATH = "/item/fluid/img"
        """
        液面控件，**相对本槽位控件**。布局改了这里要跟着改，找不到会记一条日志。

        放在 `/item` 里面是刻意的：`item` 那层挂着 `#<prefix>.item.visible` 绑定，
        空格时整层隐藏 —— 液面跟着一起消失，不用另写一份可见性逻辑。
        """

        # 液面比例的分母：`None` = 画满。
        # minijei 取的是**同方向里体积最大的那个流体**（`define.py::RenderInit`），
        # 那是「多流体产出时看得出相对多少」的约定，需要整条配方的上下文 ——
        # 单格渲染拿不到，所以由调用方经 `SetMaxVolume()` 传进来。
        # **不传就画满**：单流体格在 minijei 里本来就是满的（分母是它自己）。

        def __init__(self, control):
            self.FluidImage = None
            self.MaxVolume = None
            # 基类的 __init__ 里会调 InitControls, 所以纯数据属性必须前置
            # (引擎会吞构造异常并保留半成品实例, CLAUDE.md 引擎结论 §7)
            ItemPanel.__init__(self, control)

        def InitControls(self):
            # 路径与内置槽位完全一致(`/item/renderer`), 所以基类原样能用 ——
            # fluid_slot 是 `@mei_common.slot_base` 组装出来的, 不是另起炉灶
            ItemPanel.InitControls(self)
            image = self.Control.GetChildByPath(self.FLUID_IMG_PATH)
            if image is None:
                bridge.Error("流体槽缺少 {} —— 布局改过?".format(self.FLUID_IMG_PATH))
                return
            self.FluidImage = image.asImage()

        def SetMaxVolume(self, max_volume):  # type: (float) -> any
            """ 设置液面比例的分母，返回 self（接在 render_slot 后面写）。None = 画满 """
            self.MaxVolume = float(max_volume) if max_volume else None
            if self.Stack is not None:
                self.RenderFluid()
            return self

        def SetItemStack(self, item_stack):
            self.Stack = item_stack
            self.Item = item_stack.Item
            if not self.Item:
                return False

            # 不画物品图标: 流体是隐藏方块, SetUiItem 出来的是个方块图标, 不是我们要的
            self.ItemRendererVisible = False
            # 复用堆叠数那条绑定写体积 —— 少一条绑定就少一份每帧开销
            # (binding_cost.md: 每个槽位已经挂了 6 条, 其中 5 条是最贵的 always 档)
            self.LabelText = FormatVolume(item_stack.Count)
            self.LabelVisible = True

            self.RenderFluid()
            self.RefreshHoverText()
            return True

        def RenderFluid(self):
            """
            推液面。**失败就算了** —— 少一格预览远好过整页崩，
            而这是绑定回调里的代码：抛出去会把那条绑定一起带走且引擎不给日志
            （CLAUDE.md 引擎结论 §15）。
            """
            if self.FluidImage is None or self.Stack is None:
                return
            fluid_id = self.Item.ItemId
            try:
                path, rgb, alpha = Texture(fluid_id)
                self.FluidImage.SetSprite(path)
                self.FluidImage.SetSpriteColor((rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0))
                self.FluidImage.SetAlpha(alpha / 255.0)
                # 蔚蓝的流体贴图是竖排的序列帧, 不裁就会把整条压扁画出来; 预览只取第一帧
                self.FluidImage.SetSpriteUV((0, 0))
                self.FluidImage.SetSpriteUVSize((FRAME_SIZE, FRAME_SIZE))

                ratio = 1.0 if not self.MaxVolume else min(
                    1.0, float(self.Stack.Count) / self.MaxVolume)
                # 液面靠**撑高度**，与机器界面的 `FluidDisplayer.update` 一致。
                # 气体从上往下长，所以锚点反过来。
                #
                # ⚠ 官方签名是 `SetFullSize(axis, paramDict)`，**paramDict 的键是驼峰**；
                # 蔚蓝写的 `UICtrlPosData(...)` 是 ToolDelta 的包装器
                # （`tooldelta/ui/elem_comp.py:171`，`to_dict()` 干的就是下划线→驼峰）——
                # 照抄类名会 NameError，照抄下划线键名会静默不生效（`engineering.md` §5.1b）。
                anchor = "top_middle" if IsGas(fluid_id) else "bottom_middle"
                self.FluidImage.SetAnchorFrom(anchor)
                self.FluidImage.SetAnchorTo(anchor)
                self.FluidImage.SetFullSize(
                    "y", {"followType": "parent", "relativeValue": ratio})
            except Exception as e:  # noqa
                bridge.Error("流体渲染失败 {}: {}".format(fluid_id, bridge.ErrorText(e)))
                self.FluidImage = None      # 别每次回调再试一次

        def RefreshHoverText(self):
            """
            物品名（流体是隐藏 Item，有名字）+ 使用方的 lore + 体积。

            体积**追加在最后**，不能写进 `self.ItemLore` —— 那是使用方的地盘，
            `SetLore()` 会整个覆盖它，写进去等于把体积和使用方的说明互相顶掉。
            """
            ItemPanel.RefreshHoverText(self)
            if self.Stack is not None:
                self.ItemHoverText += (
                    NEWLINE + "§a体积: §f" + FormatVolume(self.Stack.Count))

    return FluidPanel
