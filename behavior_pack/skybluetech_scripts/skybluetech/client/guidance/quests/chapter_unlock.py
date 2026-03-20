# coding=utf-8
from mod_log import logger
from ....common.events.guidance import ChapterUnlockEvent


@ChapterUnlockEvent.Listen()
def onChapterUnlockEvent(event):
    # type: (ChapterUnlockEvent) -> None
    from ..book.base import BookMgr, BOOK_IDENTIFIER

    book = BookMgr.GetBookInstance(BOOK_IDENTIFIER)
    if book is None:
        logger.error("SkyblueTech: Book not found: " + BOOK_IDENTIFIER)
        return
    entry = book.GetEntry(event.chapter_id)
    if entry is None:
        logger.error("SkyblueTech: Book::Entry not found: " + event.chapter_id)
        return
    entry.Unlock()
