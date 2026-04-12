# coding=utf-8
import time
from skybluetech_scripts.tooldelta.api.client import GetConfigData, SetConfigData
from .page_group import PageGroup, GetPageGroup


class BookMark(object):
    def __init__(self, page_group, page_index, create_time):
        # type: (PageGroup, int, int) -> None
        self.page_group = page_group
        self.page_index = page_index
        self.create_time = create_time


class BookMarkMgr(object):
    _instance = None

    def __init__(self):
        self.raw_datas = _get_bookmarks()
        bookmarks = []  # type: list[BookMark]
        for mark, create_time in self.raw_datas.items():
            page_id, page_index = mark.split("::")
            page_group = GetPageGroup(page_id)
            if page_group is not None:
                bookmarks.append(BookMark(page_group, int(page_index), create_time))
        self.bookmarks = bookmarks
        BookMarkMgr._instance = self

    def GetBookMarks(self):
        return self.bookmarks

    def AddBookMark(self, page_group, page_index):
        # type: (PageGroup, int) -> bool
        key = "%s::%d" % (page_group.id, page_index)
        if key in self.raw_datas:
            return False
        create_time = int(time.time())
        self.bookmarks.append(BookMark(page_group, page_index, create_time))
        self.raw_datas[key] = create_time
        _set_bookmarks(self.raw_datas)
        return True

    def RemoveBookMark(self, book_mark):
        # type: (BookMark) -> bool
        try:
            self.bookmarks.remove(book_mark)
        except ValueError:
            return False
        del self.raw_datas["%s::%d" % (book_mark.page_group.id, book_mark.page_index)]
        _set_bookmarks(self.raw_datas)
        return True

    def PageIsMarked(self, page_group, page_index):
        # type: (PageGroup, int) -> bool
        return "%s::%d" % (page_group.id, page_index) in self.raw_datas

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = BookMarkMgr()
        return cls._instance


def _get_bookmarks():
    # type: () -> dict[str, int]
    return GetConfigData("st:bookmarks") or {}


def _set_bookmarks(bookmarks):
    # type: (dict[str, int]) -> None
    SetConfigData("st:bookmarks", bookmarks)
