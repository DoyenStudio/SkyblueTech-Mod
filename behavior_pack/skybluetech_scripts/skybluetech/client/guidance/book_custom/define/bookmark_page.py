# coding=utf-8
import time
from skybluetech_scripts.tooldelta.api.client import GetConfigData, SetConfigData
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from .base_page import BasePage
from .text_page import TextPage
from .page_group import PageGroup
from .book_mark import BookMark, BookMarkMgr


class BookMarkSection(object):
    def __init__(self, book_mark):
        # type: (BookMark) -> None
        self.book_mark = book_mark
        self.title = book_mark.page_group.id
        for page in book_mark.page_group.GetPages():
            if isinstance(page, TextPage):
                self.title = page.title
                break


class BookMarkPage(BasePage):
    ctrl_def_name = "GuidanceLib.book_mark_page"

    def __init__(self):
        # type: () -> None
        BasePage.__init__(self)

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None
        BasePage.RenderInit(self, ctrl)
        sections = self.load_sections()

        def render():
            grid = ctrl["sections_grid"].asGrid()

            def on_remove_bookmark(book_mark):
                # typing: (BookMark) -> None
                BookMarkMgr.instance().RemoveBookMark(book_mark)
                render()

            def on_goto_page(book_mark):
                # type: (BookMark) -> None
                book_mark.page_group.FastJump(book_mark.page_index)

            def after():
                for i, section in enumerate(sections):

                    def get_goto_handler(
                        section,  # type: BookMarkSection
                    ):
                        return lambda _: on_goto_page(section.book_mark)

                    def get_remove_handler(
                        section,  # type: BookMarkSection
                    ):
                        return lambda _: on_remove_bookmark(section.book_mark)

                    e = grid.GetGridItem(0, i)
                    e["label"].asLabel().SetText(section.title)
                    e["goto_btn"].asButton().SetCallback(get_goto_handler(section))
                    e["remove_btn"].asButton().SetCallback(get_remove_handler(section))

            grid.SetDimensionAndCall((1, len(sections)), after)

        render()

    def load_sections(self):
        return [BookMarkSection(b) for b in BookMarkMgr.instance().GetBookMarks()]


def AddBookMark(page_group, page_index):
    # type: (PageGroup, int) -> None
    data = _get_bookmarks()
    data["%s::%d" % (page_group.id, page_index)] = int(time.time())
    _set_bookmarks(data)


def _get_bookmarks():
    # type: () -> dict[str, int]
    return GetConfigData("st:bookmarks") or {}


def _set_bookmarks(bookmarks):
    # type: (dict[str, int]) -> None
    SetConfigData("st:bookmarks", bookmarks)
