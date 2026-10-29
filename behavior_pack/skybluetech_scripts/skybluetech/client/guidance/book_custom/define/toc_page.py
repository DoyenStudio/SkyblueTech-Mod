# coding=utf-8
from .base_page import BasePage
from .utils import UnfinishedItemName

if 0 > 1:
    import typing

    from .page_group import PageGroup




class TOCPageSection(object):
    def __init__(self, icon_item_id, icon_item_aux, title, link_to, link_page_index=0):
        # type: (str, int, str | None, PageGroup | typing.Callable[[], PageGroup], int) -> None
        self.icon_item_id = icon_item_id
        self.icon_item_aux = icon_item_aux
        self.title = (
            title
            if title is not None
            else UnfinishedItemName(icon_item_id)
        )
        self.link_to = link_to
        self.link_page_index = link_page_index


class TOCPage(BasePage):
    ctrl_def_name = "GuidanceLib.toc_page"

    _marked_tocpages = {}  # type: dict[str, TOCPage]

    def __init__(self, sections, identifier=None):
        # type: (list[TOCPageSection], str | None) -> None
        BasePage.__init__(self)
        self.sections = sections
        self.identifier = identifier
        if identifier is not None:
            TOCPage._marked_tocpages[identifier] = self

    def AddSection(self, section):
        # type: (TOCPageSection) -> None
        self.sections.append(section)

    @classmethod
    def GetByIdentifier(cls, identifier):
        # type: (str) -> TOCPage | None
        return cls._marked_tocpages.get(identifier)

    def SetGroup(self, group):
        # type: (PageGroup) -> None
        for s in self.sections:
            if s.link_to.GetParent() is None:
                s.link_to.SetParent(group)
        BasePage.SetGroup(self, group)

    def _on_select_section(self, index):
        # type: (int) -> None
        link_to = self.sections[index].link_to
        link_page_index = self.sections[index].link_page_index
        if callable(link_to):
            link_to = link_to()
        link_to.FastJump(link_page_index)
