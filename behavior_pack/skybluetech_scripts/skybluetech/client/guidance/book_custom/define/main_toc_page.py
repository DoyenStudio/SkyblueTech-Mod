# coding=utf-8
from ..define.page_group import PageGroup
from .base_page import BasePage
from .utils import UnfinishedItemName

if 0 > 1:
    import typing

    from .page_group import PageGroup


class MainTOCPageSection(object):
    def __init__(self, icon_item_id, icon_item_aux, title, link_to):
        # type: (str, int, str | None, PageGroup | typing.Callable[[], PageGroup]) -> None
        self.icon_item_id = icon_item_id
        self.icon_item_aux = icon_item_aux
        self.title = (
            title if title is not None else UnfinishedItemName(icon_item_id)
        )
        self.link_to = link_to


class MainTOCPage(BasePage):
    ctrl_def_name = "GuidanceLib.main_toc_page"

    _marked_tocpages = {}  # type: dict[str, MainTOCPage]

    def __init__(self, sections, identifier=None):
        # type: (list[MainTOCPageSection], str | None) -> None
        BasePage.__init__(self)
        self.sections = sections
        self.identifier = identifier
        if identifier is not None:
            self._marked_tocpages[identifier] = self

    def AddSection(self, section):
        # type: (MainTOCPageSection) -> None
        self.sections.append(section)

    @classmethod
    def GetByIdentifier(cls, identifier):
        # type: (str) -> MainTOCPage | None
        return cls._marked_tocpages.get(identifier)

    def on_select_section(self, index):
        # type: (int) -> None
        link_to = self.sections[index].link_to
        if callable(link_to):
            link_to = link_to()
        link_to.FastJump(0)

    def SetGroup(self, group):
        # type: (PageGroup) -> None
        for s in self.sections:
            s.link_to.SetParent(group)
        BasePage.SetGroup(self, group)

    def __repr__(self):
        return "MainTOCPage(%s)" % str([s.link_to for s in self.sections])
