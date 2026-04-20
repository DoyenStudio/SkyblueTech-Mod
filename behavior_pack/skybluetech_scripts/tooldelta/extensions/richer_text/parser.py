# coding=utf-8
import re
from ...utils.py_comp import py2_unicode
from .define import Option, NewLine, Text, Image, ItemRender, HyperLink, Style

tag_parser = re.compile(
    py2_unicode(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))'), re.UNICODE
)


def parse_to_group(text):
    # type: (str) -> list[tuple[bool, str]]
    cached_param = ""
    groups = []  # type: list[tuple[bool, str]]
    ignore_flag = False
    text = text.replace("\n\n", "\n \n")
    for char in text:
        if ignore_flag:
            cached_param += char
            ignore_flag = False
        elif char == "\\":
            ignore_flag = True
            continue
        elif char == "\n":
            groups.append((False, cached_param))
            cached_param = ""
            groups.append((True, "br"))
            continue
        elif char == "<":
            groups.append((False, cached_param))
            cached_param = ""
        elif char == ">":
            groups.append((True, cached_param))
            cached_param = ""
        else:
            cached_param += char
    if cached_param.strip():
        groups.append((False, cached_param))
    return groups


def parse_tags(
    groups,  # type: list[tuple[bool, str]]
):
    res = []  # type: list[Option | NewLine | Text | Image | ItemRender | HyperLink | Style]
    for group in groups:
        is_tag, content = group
        if not is_tag:
            res.append(Text(content))
            continue
        tag_name, params = parse_tag(content)
        if tag_name == Text.name:
            # scale = params.get("scale")
            # if scale is not None:
            #     scale = float(scale)
            color = params.get("color")
            if color is not None:
                res.append(Style(color=color))
            res.append(Text(params["t"]))
            if color is not None:
                res.append(Style(color="R"))
        elif tag_name == Option.name:
            res.append(Option(params))
        elif tag_name == Style.name:
            scale = params.get("scale")
            if scale is not None:
                scale = float(scale)
            res.append(Style(params.get("color"), scale))
            continue
        elif tag_name == NewLine.name:
            res.append(NewLine())
        elif tag_name == Image.name:
            size_x = params.get("size_x")
            size_y = params.get("size_y")
            if size_x is not None:
                size_x = float(size_x)
            if size_y is not None:
                size_y = float(size_y)
            res.append(Image(params["path"], size_x, size_y))
        elif tag_name == ItemRender.name:
            scale = params.get("scale")
            if scale is not None:
                scale = float(scale)
            res.append(ItemRender(params["id"], int(params.get("aux", "0")), scale))
        elif tag_name == HyperLink.name:
            res.append(HyperLink(params["text"], params["id"]))
        else:
            print("[ERROR] Unknown tag: " + tag_name)
    return res


def parse_tag(tag_str):
    # type: (str) -> tuple[str, dict[str, str]]
    parts = tag_str.split(None, 1)
    tag_name = parts[0]
    if len(parts) < 2:
        return tag_name, {}
    param_str = parts[1]
    params = {}
    for m in tag_parser.finditer(param_str):
        key = m.group(1)
        value = m.group(2)
        if value is None:
            value = m.group(3)
        if value is None:
            value = m.group(4)
        params[key] = value
    return tag_name, params
