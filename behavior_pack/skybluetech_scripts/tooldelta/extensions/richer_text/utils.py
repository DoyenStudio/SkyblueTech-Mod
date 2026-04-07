# coding=utf-8

_wide_mark = "？＃＄％＆＇（）＊＋－／＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…﹏"

zhcn_start = ord(u"一")
zhcn_end = ord(u"龥")

RICH_TEXT_COLOR_CONVERT = {
	"§0": "#000000",
	"§1": "#0000aa",
	"§2": "#00aa00",
	"§3": "#00aaaa",
	"§4": "#aa0000",
	"§5": "#aa00aa",
	"§6": "#ffaa00",
	"§7": "#aaaaaa",
	"§8": "#555555",
	"§9": "#5555ff",
	"§a": "#55ff55",
	"§b": "#55ffff",
	"§c": "#ff5555",
	"§d": "#ff55ff",
	"§e": "#ffff55",
	"§f": "#ffffff",
	"§g": "#ddd605",
	"§h": "#e3d4d1",
	"§i": "#cecaca",
	"§j": "#443a3b",
	"§m": "#971607",
	"§n": "#b4684d",
	"§p": "#deb12d",
	"§q": "#47a036",
	"§s": "#2cbaa8",
	"§t": "#21497b",
	"§u": "#9a5cc6",
}

def is_chinese(string):
    # type: (str) -> bool
    return any(
        (char in _wide_mark) or (zhcn_start <= ord(char) <= zhcn_end) for char in string
    )

def color_convert(color_format):
    # type: (str) -> tuple[float, float, float]
    res = RICH_TEXT_COLOR_CONVERT.get(str(color_format))
    if res is None:
        return (-1, -1, -1)
    color_hex = res[1:]
    r = int(color_hex[0:2], 16) / 255.0
    g = int(color_hex[2:4], 16) / 255.0
    b = int(color_hex[4:6], 16) / 255.0
    return (r, g, b)