# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.richer_text import (
    RicherTextCtrl,
    RicherTextOpt,
)
from .base_page import BasePage

if 0:
    import typing


class TextPage(BasePage):
    ctrl_def_name = "GuidanceLib.text_page"

    def __init__(self, page_id, title, content, hyperlink_cbs=None):
        # type: (str, str, str, dict[str, typing.Callable[[dict], None]] | None) -> None
        BasePage.__init__(self, page_id)
        self.title = title
        self.content = content
        self.hyperlink_cbs = hyperlink_cbs or {}

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None
        BasePage.RenderInit(self, ctrl)
        ctrl["title_label"].asLabel().SetText(self.title)
        async_executor = RicherTextCtrl(
            ctrl["content"], opts=RicherTextOpt(hyperlink_cbs=self.hyperlink_cbs)
        ).SetTextAsync(self.content)

        def run_async():
            if run_async.finished:
                return
            try:
                next(async_executor)
            except StopIteration:
                run_async.finished = True

        run_async.finished = False
        ctrl._root.AddOnTickingCallback(run_async)
