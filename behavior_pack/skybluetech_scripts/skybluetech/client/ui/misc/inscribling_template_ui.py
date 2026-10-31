# coding=utf-8
from mod.client.extraClientApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame
from skybluetech_scripts.tooldelta.ui import (
    RegistToolDeltaScreen,
    Binder,
    ToolDeltaScreen,
)
from skybluetech_scripts.skybluetech.common.events.misc.inscribling_template import (
    InscribingTemplateGraphUpload,
)
from skybluetech_scripts.skybluetech.common.misc.inscribing_template import (
    K_UI_TEMPLATE_GRAPH,
)

KeyEnum = GetMinecraftEnum().KeyBoardType
_ESCAPE = KeyEnum.KEY_ESCAPE


@RegistToolDeltaScreen("InscribingTemplateUI.main")
class InscribingTemplateUI(ToolDeltaScreen):
    def __init__(self, screen_name, screen_instance, params):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        self.graph = params[K_UI_TEMPLATE_GRAPH]  # type: list[int]
        self.current_icon_element_section = 0
        self.current_graph_element_section = 0

    @Binder.binding(
        Binder.BF_ButtonClickDown,
        "#InscribingTemplateUI.close_btn",
    )
    def on_close_btn_click(self, params):
        # type: (dict) -> None
        self.RemoveUI()

    @Binder.binding(
        Binder.BF_ButtonClickDown,
        "#InscribingTemplateUI.template_element_button",
    )
    def on_click_graph_item(self, params):
        # type: (dict) -> None
        self.current_graph_element_section = params["#collection_index"]

    @Binder.binding(
        Binder.BF_ButtonClickDown,
        "#InscribingTemplateUI.template_section_button",
    )
    def on_click_section_item(self, params):
        # type: (dict) -> None
        self.current_icon_element_section = params["#collection_index"]
        self.graph[self.current_graph_element_section] = (
            self.current_icon_element_section
        )
        InscribingTemplateGraphUpload(self.graph).send()

    # @Binder.binding_collection(
    #     Binder.BF_BindGridSize,
    #     "inscribing_template_sections_grid",
    #     "#InscribingTemplateUI.template_section_icon_uv",
    # )
    # def get_section_element_uv(self, index):
    #     # type: (int) -> tuple[int, int]
    #     print("ELEM UV", index)
    #     return (index * 16, 0)

    @Binder.binding_collection(
        Binder.BF_BindString,
        "inscribing_template_sections_grid",
        "#InscribingTemplateUI.template_section_icon_texture",
    )
    def get_section_element_icon_texture(self, index):
        # type: (int) -> str
        return "textures/ui/skybluetech/inscribing_element_icon_" + str(index + 1)

    @Binder.binding_collection(
        Binder.BF_BindBool,
        "inscribing_template_sections_grid",
        "#InscribingTemplateUI.template_section_border_visible",
    )
    def get_section_element_border_visible(self, index):
        # type: (int) -> bool
        return index == self.current_icon_element_section

    @Binder.binding_collection(
        Binder.BF_BindString,
        "inscribing_template_graph_grid",
        "#InscribingTemplateUI.template_element_base_texture",
    )
    def get_graph_element_base_texture(self, index):
        # type: (int) -> str
        return (
            "textures/ui/skybluetech/inscribing_template_ui_graph_element_base_focused"
            if index == self.current_graph_element_section
            else "textures/ui/skybluetech/inscribing_template_ui_graph_element_base_unfocused"
        )

    # @Binder.binding_collection(
    #     Binder.BF_BindGridSize,
    #     "inscribing_template_graph_grid",
    #     "#InscribingTemplateUI.template_element_icon_uv",
    # )
    # def get_graph_element_icon_uv(self, index):
    #     # type: (int) -> tuple[int, int]
    #     print("graph", index)
    #     return (self.graph[index] * 16, 0)

    @Binder.binding_collection(
        Binder.BF_BindString,
        "inscribing_template_graph_grid",
        "#InscribingTemplateUI.template_element_icon_texture",
    )
    def get_graph_element_icon_texture(self, index):
        # type: (int) -> str
        return "textures/ui/skybluetech/inscribing_element_icon_" + str(self.graph[index] + 1)

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def on_key_press(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.key == _ESCAPE and event.isDown:
            self.RemoveUI()
