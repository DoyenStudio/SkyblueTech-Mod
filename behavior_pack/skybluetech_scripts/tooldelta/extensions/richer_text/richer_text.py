# coding=utf-8
from ...define import Item
from ...ui import UBaseCtrl
from .parser import (
    Option,
    Style,
    NewLine,
    Text,
    Image,
    ItemRender,
    HyperLink,
    parse_tags,
    parse_to_group,
)
from .utils import is_chinese

if 0:
    import typing

    HYPERLINK_CB = typing.Callable[[dict], None]


class RicherTextOpt(object):
    def __init__(self, hyperlink_cbs=None):
        # type: (dict[str, HYPERLINK_CB] | None) -> None
        self.hyperlink_cbs = hyperlink_cbs or {}


class RicherTextCtrl(object):
    ui_def_name = "richer_text.RicherTextPanel"

    def __init__(self, ctrl, opts=None):
        # type: (UBaseCtrl, RicherTextOpt | None) -> None
        self.ctrl = ctrl
        self.opts = opts or RicherTextOpt()
        self._simulate_text = ctrl["simulate_text"].asLabel()
        self._simulate_image = ctrl["simulate_image"].asImage()
        self._simulate_hyperlink_btn = ctrl["simulate_hyperlink_btn"].asButton()
        self._simulate_item_renderer = ctrl["simulate_item_renderer"].asItemRenderer()
        self._size_x, self._size_y = ctrl.GetSize()
        self._process_x = 0
        self._process_y = 0
        self._current_row_max_y = 0
        self.ctrl_counter = 0
        self._hang_ctrls = []  # type: list[UBaseCtrl]
        self._current_text_scale = None
        r, g, b, _ = self._simulate_text.base.GetTextColor()
        self._initial_text_color = (r, g, b)
        self._current_color = self._initial_text_color
        self._line_spacing = 0
        # pre-load

    def SetText(self, text):
        # type: (str) -> None
        # py2 = unicode
        # py3 = str
        self._clean()
        content = text.decode("utf-8") if isinstance(text, bytes) else text
        self._process_content(content)

    def SetTextAsync(
        self,
        text,  # type: str
    ):
        self._clean()
        content = text.decode("utf-8") if isinstance(text, bytes) else text
        return self._process_content_async(content)

    def _process_content(self, content):
        # type: (str) -> None
        for old_ctrl in self._hang_ctrls:
            old_ctrl.Remove()
        self._hang_ctrls = []
        self._process_x = 0
        self._process_y = 0
        group = parse_to_group(content)
        elements = parse_tags(group)
        for e in elements:
            if isinstance(e, Option):
                self._process_option(e)
            elif isinstance(e, NewLine):
                self._new_line()
            elif isinstance(e, Text):
                self._process_dirty_text(e.content)
            elif isinstance(e, Image):
                self._put_image(e)
            elif isinstance(e, ItemRender):
                self._put_item_renderer(e)
            elif isinstance(e, HyperLink):
                self._process_dirty_text(e.text, hyperlink=e)
            elif isinstance(e, Style):
                self._process_style(e)
            else:
                raise ValueError("[ERROR] unknown element type")
        self._finish()

    def _process_content_async(
        self,
        content,  # type: str
    ):
        for old_ctrl in self._hang_ctrls:
            old_ctrl.Remove()
        self._hang_ctrls = []
        self._process_x = 0
        self._process_y = 0
        group = parse_to_group(content)
        elements = parse_tags(group)
        for e in elements:
            if isinstance(e, Option):
                self._process_option(e)
            elif isinstance(e, NewLine):
                self._new_line()
            elif isinstance(e, Text):
                self._process_dirty_text(e.content)
            elif isinstance(e, Image):
                self._put_image(e)
            elif isinstance(e, ItemRender):
                self._put_item_renderer(e)
            elif isinstance(e, HyperLink):
                self._process_dirty_text(e.text, hyperlink=e)
            elif isinstance(e, Style):
                self._process_style(e)
            else:
                raise ValueError("[ERROR] unknown element type")
            yield
        self._finish()

    def _process_option(self, option):
        # type: (Option) -> None
        opt = option.params["name"]
        if opt == "line_spacing":
            self._line_spacing = float(option.params["val"])

    def _process_dirty_text(self, text, hyperlink=None):
        # type: (str, HyperLink | None) -> None
        _text = text
        repeat_count = 0
        while _text:
            repeat_count += 1
            if repeat_count >= 50:
                raise ValueError("[ERROR] repeat count >= 50")
            end_index = 0
            diff_flag = is_chinese(_text[0])
            for idx, char in enumerate(_text[1:]):
                if is_chinese(char) != diff_flag:
                    end_index = idx + 1
                    break
            if end_index == 0:
                self._process_aligned_text(_text, hyperlink)
                break
            else:
                self._process_aligned_text(_text[:end_index], hyperlink)
                _text = _text[end_index:]

    def _process_aligned_text(self, text, hyperlink=None, depth=0):
        # type: (str, HyperLink | None, int) -> None
        if depth > 20:
            raise ValueError("[ERROR] depth >= 20")
        self._simulate_text.SetText(str(text), sync_size=True)
        size_x, _ = self._simulate_text.GetSize()
        if self._enough_for_space(size_x):
            text_ctrl = self._put_text()
            if hyperlink is not None:
                self._put_hyperlink(hyperlink, text_ctrl)
        else:
            single_char_size_x = int(size_x / len(text))
            eof_index = int(self._get_space_left() / single_char_size_x)
            self._simulate_text.SetText(text[:eof_index], sync_size=True)
            text_ctrl = self._put_text(auto_new_line=False)
            if hyperlink is not None:
                self._put_hyperlink(hyperlink, text_ctrl)
            self._new_line()
            if text[eof_index:]:
                self._process_aligned_text(text[eof_index:], hyperlink, depth + 1)

    def _process_style(self, style):
        # type: (Style) -> None
        if style.color == (-1, -1, -1):
            self._simulate_text.SetColor(self._initial_text_color)
        elif style.color is not None:
            self._simulate_text.SetColor(style.color)
        if style.scale is not None:
            self._current_text_scale = style.scale
        else:
            self._current_text_scale = None

    def _enough_for_space(self, size_x):
        # type: (float) -> bool
        return self._process_x + size_x <= self._size_x

    def _get_space_left(self):
        # type: () -> float
        return self._size_x - self._process_x

    def _put_text(self, auto_new_line=True):
        ctrl = self._simulate_text.clone(self._gen_name())
        if self._current_text_scale is not None:
            ctrl.base.SetTextFontSize(self._current_text_scale)
        self._put_control(ctrl, self._simulate_text, auto_new_line=auto_new_line)
        return ctrl

    def _put_image(
        self,
        image,  # type: Image
        # img_path,  # type: str
        # size_xy,  # type: tuple[float, float]
        # color=None,  # type: tuple[float, float, float] | None
    ):
        img = self._simulate_image.clone(self._gen_name())
        y_scale = image.y_scale or self._current_row_max_y or 20
        x_scale = image.x_scale or y_scale
        img.SetSize((x_scale, y_scale))
        img.SetSprite(image.path)
        self._put_control(img, img)
        return img

    def _put_item_renderer(
        self,
        item_render,  # type: ItemRender
    ):
        item_renderer = self._simulate_item_renderer.clone(self._gen_name())
        item_renderer.SetUiItem(Item(item_render.item_id, item_render.item_aux))
        scale = item_render.scale or self._current_row_max_y or 2
        item_renderer.SetSize((scale, scale))
        self._put_control(item_renderer, item_renderer)
        return item_renderer

    def _put_control(self, ctrl, template, auto_new_line=True):
        # type: (UBaseCtrl, UBaseCtrl, bool) -> None
        size_x, size_y = template.GetSize()
        self._current_row_max_y = max(self._current_row_max_y, size_y)
        if self._get_space_left() < size_x and auto_new_line:
            self._new_line()
        ctrl.SetPos((self._process_x, self._process_y))
        self._process_x += size_x
        self._hang_ctrls.append(ctrl)
        ctrl.SetVisible(True)

    def _put_hyperlink(self, hyperlink, ctrl):
        # type: (HyperLink, UBaseCtrl) -> None
        cb = self.opts.hyperlink_cbs.get(hyperlink.id)
        if not cb:
            return
        btn = self._simulate_hyperlink_btn.clone(self._gen_name())
        btn.SetCallback(cb)
        btn.SetPos(ctrl.GetPos())
        btn.SetSize(
            self._simulate_text.GetSize(), resize_children=True
        )  # 实在没招了, 此时 ctrl 的 size 是 0
        btn.SetLayer(90)
        self._hang_ctrls.append(btn)

    def _gen_name(self):
        self.ctrl_counter += 1
        return "ctrl_" + str(self.ctrl_counter)

    def _test_new_line(self):
        if self._get_space_left() <= 0:
            self._new_line()

    def _new_line(self):
        if self._current_row_max_y == 0:
            print("[WARNING] seems no controls in this line")
        self._process_x = 0
        self._process_y += self._current_row_max_y + self._line_spacing
        self._current_row_max_y = 0

    def _finish(self):
        pass
        # self._simulate_text.SetVisible(False)
        # self._simulate_image.SetVisible(False)
        # self._simulate_hyperlink_btn.SetVisible(False)
        # self._simulate_item_renderer.SetVisible(False)

    def _clean(self):
        for ctrl in self._hang_ctrls:
            ctrl.Remove()
        self._hang_ctrls = []
        self._process_x = 0
        self._process_y = 0
        self._current_row_max_y = 0
        self._simulate_text.SetVisible(True)
        self._simulate_image.SetVisible(True)
        self._simulate_hyperlink_btn.SetVisible(True)
        self._simulate_item_renderer.SetVisible(True)
