# coding=utf-8
from collections import deque
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import (
    Binder,
    ToolDeltaScreen,
    RegistToolDeltaScreen,
    SCREEN_BASE_PATH,
)
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame

if 0>1:
    from ...guidance.book_custom.define import BasePage, PageGroup


@RegistToolDeltaScreen("SkyblueTechGuidanceUI.main")
class GuidanceUI(ToolDeltaScreen):
    current_instance = None

    def __init__(self, screen_name, screen_instance, params=None):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        if params is not None:
            self.initial_page_group = params.get("main_pages")  # type: PageGroup
        else:
            raise ValueError("Create GuidanceUI: params=None")
        self.page_index = 0
        self._left_page_content = None
        self._right_page_content = None
        self.left_page_instance = None
        self.right_page_instance = None
        self.current_page_group = self.initial_page_group
        GuidanceUI.current_instance = self

    def OnCreate(self):
        self.left_page = self.GetElement(SCREEN_BASE_PATH / "full_page/left_page")
        self.right_page = self.GetElement(SCREEN_BASE_PATH / "full_page/right_page")
        self.prev_page_btn = (
            self
            .GetElement(SCREEN_BASE_PATH / "prev_page_btn")
            .asButton()
            .SetCallback(self.on_click_prev_page)
        )
        self.next_page_btn = (
            self
            .GetElement(SCREEN_BASE_PATH / "next_page_btn")
            .asButton()
            .SetCallback(self.on_click_next_page)
        )
        self.back_btn = (
            self
            .GetElement(SCREEN_BASE_PATH / "back_btn")
            .asButton()
            .SetCallback(self.on_click_back)
        )
        self.close_btn = (
            self
            .GetElement(SCREEN_BASE_PATH / "close_btn")
            .asButton()
            .SetCallback(self.on_click_close)
        )
        self.render_page()

    def OnDestroy(self):
        if self.left_page_instance is not None and self._left_page_content is not None:
            self.left_page_instance.DeRender(self._left_page_content)
        if self.right_page_instance is not None and self._right_page_content is not None:
            self.right_page_instance.DeRender(self._right_page_content)
        GuidanceUI.current_instance = None
        self.left_page_instance = None
        self.right_page_instance = None
        self._left_page_content = None
        self._right_page_content = None

    def OnTicking(self):
        if self.left_page_instance:
            self.left_page_instance.ScreenTicking()
        if self.right_page_instance:
            self.right_page_instance.ScreenTicking()

    @Binder.binding(
        Binder.BF_SliderChanged | Binder.BF_SliderFinished,
        "#guidance.structure_model_size",
    )
    def on_structure_model_size_changed(self, _progress, _finished, _index):
        from ...guidance.book_custom.define.multi_block_structure_model_page import (
            MultiBlockStructureModelPage,
        )

        # 两页可以同时展示模型，读取各自控件，只更新实际发生变化的一页。
        for page in (self.left_page_instance, self.right_page_instance):
            if isinstance(page, MultiBlockStructureModelPage):
                page.UpdateSizeFromSlider()

    def render_page(self):
        from ...guidance.book_custom.define import MainTOCPage, TOCPage

        self._unbind_toc_page("left")
        self._unbind_toc_page("right")
        if self._left_page_content is not None:
            if self.left_page_instance is not None:
                self.left_page_instance.DeRender(self._left_page_content)
            self._left_page_content.Remove()
            self._left_page_content = None
        if self._right_page_content is not None:
            if self.right_page_instance is not None:
                self.right_page_instance.DeRender(self._right_page_content)
            self._right_page_content.Remove()
            self._right_page_content = None

        pages = self.current_page_group.GetPages()
        self.left_page_instance = self.right_page_instance = None
        for i, page in enumerate(pages[self.page_index : self.page_index + 2]):
            side = "left" if i == 0 else "right"
            ctrl_def_name = page.ctrl_def_name
            if isinstance(page, (MainTOCPage, TOCPage)):
                # 动态创建的控件不继承外部容器变量，使用自带绑定变量的模板。
                ctrl_def_name += "_" + side
            # 在创建控件前注册，保证首次绑定查询就能取得当前页的数据。
            self._bind_toc_page(page, side)
            if i == 0:
                self._left_page_content = e = self.left_page.AddElement(
                    ctrl_def_name, "page"
                )
                self.left_page_instance = page
            elif i == 1:
                self._right_page_content = e = self.right_page.AddElement(
                    ctrl_def_name, "page"
                )
                self.right_page_instance = page
            else:
                break
            page.RenderInit(e)
        self.back_btn.SetVisible(self.current_page_group.GetParent() is not None)
        self.prev_page_btn.SetVisible(self.page_index >= 2)
        self.next_page_btn.SetVisible(
            self.page_index < self.current_page_group.GetPagesNum() - 2
        )

    def _bind_toc_page(self, page, side):
        # type: (BasePage, str) -> None
        from ...guidance.book_custom.define import MainTOCPage, TOCPage
        from ...guidance.book_custom.define.utils import finish_name

        if not isinstance(page, (MainTOCPage, TOCPage)):
            return
        collection = "guidance_%s_tocs" % side
        prefix = "#guidance.%s_toc_" % side

        def get_icon(index):
            # type: (int) -> int
            if not 0 <= index < len(page.sections):
                return 131072
            section = page.sections[index]
            return Item(section.icon_item_id, section.icon_item_aux).GetBasicInfo().id_aux

        def get_title(index):
            # type: (int) -> str
            if not 0 <= index < len(page.sections):
                return ""
            return finish_name(page.sections[index].title)

        def on_select(params):
            # type: (dict) -> None
            index = params["#collection_index"]
            if not 0 <= index < len(page.sections):
                return
            if isinstance(page, MainTOCPage):
                page.on_select_section(index)
            else:
                page._on_select_section(index)

        if isinstance(page, MainTOCPage):
            self.DynaBinding(
                Binder.BF_BindInt, prefix + "count", lambda: len(page.sections)
            )
        else:
            self.DynaBinding(
                Binder.BF_BindGridSize,
                prefix + "grid_size",
                lambda: (1, len(page.sections)),
            )
        self.DynaBindingCollection(
            Binder.BF_BindInt, collection, prefix + "icon", get_icon
        )
        self.DynaBindingCollection(
            Binder.BF_BindString, collection, prefix + "title", get_title
        )
        self.DynaBinding(Binder.BF_ButtonClickUp, prefix + "select", on_select)

    def _unbind_toc_page(self, side):
        # type: (str) -> None
        collection = "guidance_%s_tocs" % side
        prefix = "#guidance.%s_toc_" % side
        self.DynaUnbinding(Binder.BF_BindInt, prefix + "count")
        self.DynaUnbinding(Binder.BF_BindGridSize, prefix + "grid_size")
        self.DynaUnbindingCollection(Binder.BF_BindInt, collection)
        self.DynaUnbindingCollection(Binder.BF_BindString, collection)
        self.DynaUnbinding(Binder.BF_ButtonClickUp, prefix + "select")

    def on_click_prev_page(self, _):
        if self.page_index >= 2:
            self.page_index -= 2
            self.render_page()

    def on_click_next_page(self, _):
        if self.page_index < self.current_page_group.GetPagesNum() - 2:
            self.page_index += 2
            self.render_page()

    def on_click_back(self, _):
        parent = self.current_page_group.GetParent()
        if parent is not None:
            self.current_page_group = parent
            self.page_index = 0
            self.render_page()

    def on_click_close(self, _):
        self.RemoveUI()

    def load_new_pages(self, pages, index=0):
        # type: (PageGroup, int) -> None
        expect_page_index = int(index // 2 * 2)
        if pages is self.current_page_group and self.page_index == expect_page_index:
            return
        self.current_page_group = pages
        self.page_index = expect_page_index
        self.render_page()

    @classmethod
    def get_instance(cls):
        return cls.current_instance

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.isDown and event.key == event.KeyBoardType.KEY_ESCAPE:
            self.RemoveUI()
