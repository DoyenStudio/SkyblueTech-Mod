# coding=utf-8
from collections import deque
from skybluetech_scripts.tooldelta.ui import (
    ToolDeltaScreen,
    RegistToolDeltaScreen,
    SCREEN_BASE_PATH,
)
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame

if 0:
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
        GuidanceUI.current_instance = None
        self._left_page_content = None
        self._right_page_content = None

    def OnTicking(self):
        if self.left_page_instance:
            self.left_page_instance.ScreenTicking()
        if self.right_page_instance:
            self.right_page_instance.ScreenTicking()

    def render_page(self):
        from ...guidance.book_custom.define import BookMarkMgr

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
            if i == 0:
                self._left_page_content = e = self.left_page.AddElement(
                    page.ctrl_def_name, "page"
                )
                self.left_page_instance = page
            elif i == 1:
                self._right_page_content = e = self.right_page.AddElement(
                    page.ctrl_def_name, "page"
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
        if pages is self.current_page_group:
            return
        self.current_page_group = pages
        self.page_index = int(index / 2)
        self.render_page()

    @classmethod
    def get_instance(cls):
        return cls.current_instance

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.isDown and event.key == event.KeyBoardType.KEY_ESCAPE:
            self.RemoveUI()
