# coding=utf-8
from skybluetech_scripts.tooldelta.ui import Binder, UBaseCtrl

from ..machinery_extra_pages.base_page import MainPage, PageBase
from .define import MAIN_PATH, MachinePanelUIProxy


class MachinePanelUIProxyEx(MachinePanelUIProxy):
    available_extra_pages = ()  # type: tuple[type[PageBase], ...]

    def __init__(self, screen_name, screen_instance, params=None):
        MachinePanelUIProxy.__init__(self, screen_name, screen_instance, params)
        self._page_cache = {}  # type: dict[type[PageBase], PageBase]
        self._current_ex_page = MainPage()
        self._current_ex_page_index = 0

    def _on_create(self):
        self._total_ex_pages = (MainPage,) + self.available_extra_pages
        self._main_path_ctrl = self.GetElement(MAIN_PATH)
        self._ex_panel_ctrl = self.GetElement(MAIN_PATH)._parent / "ex_panel"
        self.reset()
        MachinePanelUIProxy._on_create(self)

    def _on_destroy(self):
        MachinePanelUIProxy._on_destroy(self)

    def reset(self):
        sub_ctrl_names = self._ex_panel_ctrl._root.base.GetChildrenName(
            str(self._ex_panel_ctrl.getFullPath())
        )
        if sub_ctrl_names:
            for ctrl_name in sub_ctrl_names:
                self._ex_panel_ctrl[ctrl_name].Remove()
            self.GetElement(MAIN_PATH).SetVisible(True)

    def switch_page(self, page_cls):
        # type: (type[PageBase]) -> None
        if self._current_ex_page is not None:
            if isinstance(self._current_ex_page, MainPage):
                self._main_path_ctrl.SetVisible(False)
            else:
                self._current_ex_page.Deactive()
                self._current_ex_page.base.SetVisible(False)
        if page_cls is MainPage:
            self._main_path_ctrl.SetVisible(True)
            page = MainPage()
        else:
            if page_cls not in self._page_cache:
                base = self._ex_panel_ctrl.AddElement(
                    page_cls.GetControlDef(), page_cls.__name__
                )
                base.SetAnchorFrom("top_middle")
                base.SetAnchorTo("top_middle")
                page = self._page_cache[page_cls] = page_cls(base, self.pos)
                self._page_cache[page_cls].Init()
            else:
                page = self._page_cache[page_cls]
                page.base.SetVisible(True)
            page.Active()
        self._current_ex_page = page

    @Binder.binding(Binder.BF_BindGridSize, "#simple_panel_left_sections_gridsize")
    def on_get_grid_size(self):
        return (1, len(self._total_ex_pages))

    @Binder.binding_collection(
        Binder.BF_BindString,
        "simple_panel_left_sections",
        "#SkybluePanelLib.simple_left_section_icon_texture",
    )
    def on_get_grid_item_icon_texture(self, index):
        # type: (int) -> str
        return self._total_ex_pages[index].GetIconPath()

    @Binder.binding_collection(
        Binder.BF_BindString,
        "simple_panel_left_sections",
        "#SkybluePanelLib.simple_left_section_bg_texture",
    )
    def on_get_grid_bg_texture(self, index):
        # type: (int) -> str
        return (
            (
                "textures/ui/left_section_top"
                if index == 0
                else "textures/ui/left_section"
            )
            if index == self._current_ex_page_index
            else (
                "textures/ui/left_section_not_selected_top"
                if index == 0
                else "textures/ui/left_section_not_selected"
            )
        )

    @Binder.binding(
        Binder.BF_ButtonClickUp,
        "#SkybluePanelLib.simple_left_section_button_click",
    )
    def on_grid_item_button_click(self, params):
        # type: (dict) -> None
        index = params["#collection_index"]
        if index == self._current_ex_page_index:
            return
        self.switch_page(self._total_ex_pages[index])
        self._current_ex_page_index = index
