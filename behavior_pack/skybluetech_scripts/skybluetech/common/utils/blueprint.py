# coding=utf-8
"""Version 1. Cells use y, x, z order, with z changing fastest."""
import re
import struct
import zlib
from itertools import groupby
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode, py2_xrange

LIMIT = (64, 32, 64)
DIRECTIONS = ("north", "east", "south", "west")
FORWARD = ((0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0))
BASE91 = ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
          '!#$%&()*+,./:;<=>?@[]^_`{|}~"')
BASE91_DIGITS = dict((ch, i) for i, ch in enumerate(BASE91))
NAME = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+\Z")
MAX_BYTES = 2 * 1024 * 1024


def as_text(value):
    return value if isinstance(value, py2_unicode) else value.decode("utf-8")


def bounds(first, last):
    low = tuple(min(a, b) for a, b in zip(first, last))
    return low, tuple(abs(a - b) + 1 for a, b in zip(first, last))


def rotate(pos, turns):
    x, y, z = pos
    return ((x, y, z), (-z, y, x), (-x, y, -z), (z, y, -x))[turns % 4]


def local(index, size):
    y, rest = divmod(index, size[0] * size[2])
    x, z = divmod(rest, size[2])
    return x, y, z


def linear(pos, size):
    x, y, z = pos
    return (y * size[0] + x) * size[2] + z


def front(pos, facing):
    return tuple(a + b for a, b in zip(pos, FORWARD[facing]))


def material_key(name, aux):
    # NetEase's pick-block stack for chests may carry a facing aux.
    if name in ("minecraft:chest", "minecraft:trapped_chest", "minecraft:ender_chest"):
        return name, 0
    return name, aux


def world(pos, anchor, origin, turns):
    delta = rotate(tuple(a - b for a, b in zip(pos, anchor)), turns)
    return tuple(a + b for a, b in zip(origin, delta))


def uint(value):
    out = bytearray()
    while value >= 128:
        out.append(128 | (value & 127))
        value >>= 7
    out.append(value)
    return out


class Reader(object):
    def __init__(self, data):
        self.data = bytearray(data)
        self.offset = 0

    def integer(self):
        value = 0
        for shift in (0, 7, 14, 21):
            if self.offset >= len(self.data):
                break
            digit = self.data[self.offset]
            self.offset += 1
            value |= (digit & 127) << shift
            if digit < 128:
                return value
        raise ValueError("integer")

    def block(self):
        length = self.integer()
        end = self.offset + length
        if not 1 <= length <= 256 or end > len(self.data):
            raise ValueError("identifier length")
        name = bytes(self.data[self.offset:end]).decode("ascii")
        self.offset = end
        if ":" not in name:
            name = "minecraft:" + name
        if not NAME.match(name):
            raise ValueError("identifier")
        return str(name), self.integer()


def gzip_data(data):
    # A fixed gzip header makes equivalent snapshots produce identical codes.
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    raw = bytes(data)
    return (b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff" + comp.compress(raw)
            + comp.flush() + struct.pack("<II", zlib.crc32(raw) & 0xffffffff, len(raw)))


def pack(size, anchor, facing, groups):
    header = bytearray(tuple(size) + tuple(anchor) + (facing,))
    header.extend(uint(len(groups)))
    sparse, runs = bytearray(b"S") + header, bytearray(b"R") + header
    for (name, aux), indices in sorted(groups.items()):
        name = name.split(":", 1)[1] if name.startswith("minecraft:") else name
        raw = name.encode("ascii")
        entry = uint(len(raw)) + raw + uint(aux)
        indices = sorted(indices)
        sparse.extend(entry + uint(len(indices)))
        last = -1
        spans = []
        for _, run in groupby(enumerate(indices), lambda pair: pair[1] - pair[0]):
            first = end = next(run)[1]
            sparse.extend(uint(first - last - 1))
            for _, end in run:
                sparse.append(0)
            spans.append((first, end))
            last = end
        runs.extend(entry + uint(len(spans)))
        last = -1
        for first, end in spans:
            runs.extend(uint(first - last - 1) + uint(end - first))
            last = end
    return min((gzip_data(sparse), gzip_data(runs)), key=len)


def share(blob):
    """Standard basE91 over the complete gzip member."""
    output = []
    bits = value = 0
    for byte in bytearray(blob):
        value |= byte << bits
        bits += 8
        if bits > 13:
            width = 13 if (value & 8191) > 88 else 14
            pair = value & ((1 << width) - 1)
            output.extend((BASE91[pair % 91], BASE91[pair // 91]))
            value >>= width
            bits -= width
    if bits:
        output.append(BASE91[value % 91])
        if bits > 7 or value > 90:
            output.append(BASE91[value // 91])
    return "".join(output)


def unshare(code):
    code = as_text(code)
    if not 0 < len(code) <= 500:
        raise ValueError("format")
    raw = bytearray()
    bits = value = 0
    first = None
    for ch in code:
        digit = BASE91_DIGITS.get(ch)
        if digit is None:
            raise ValueError("alphabet")
        if first is None:
            first = digit
            continue
        pair = first + 91 * digit
        first = None
        value |= pair << bits
        bits += 13 if (pair & 8191) > 88 else 14
        while bits >= 8:
            raw.append(value & 255)
            value >>= 8
            bits -= 8
    if first is not None:
        raw.append((value | (first << bits)) & 255)
    blob = bytes(raw)
    if share(blob) != code:
        raise ValueError("padding")
    try:
        return unpack(blob)
    except (zlib.error, struct.error):
        raise ValueError("gzip")


def unpack(blob):
    stream = zlib.decompressobj(31)
    # A sentinel verifies end-of-stream on Python 2 (no decompressobj.eof).
    raw = stream.decompress(blob + b"!", MAX_BYTES + 1)
    if stream.unused_data != b"!" or len(raw) > MAX_BYTES or len(raw) < 9:
        raise ValueError("gzip")
    r = Reader(raw)
    mode = raw[:1]
    size, anchor = tuple(r.data[1:4]), tuple(r.data[4:7])
    facing = r.data[7]
    if (mode not in (b"S", b"R") or facing > 3
            or any(not 0 < n <= cap for n, cap in zip(size, LIMIT))
            or any(a not in (0, n - 1) for a, n in zip(anchor, size))):
        raise ValueError("bounds")
    volume = size[0] * size[1] * size[2]
    r.offset = 8
    count = r.integer()
    if not 1 <= count <= volume:
        raise ValueError("palette")
    groups, used = {}, set()
    for _ in py2_xrange(count):
        key = r.block()
        if key in groups or key[1] > 0xffff:
            raise ValueError("palette entry")
        indices = groups[key] = []
        last = -1
        spans = r.integer()
        if not 1 <= spans <= volume:
            raise ValueError("span count")
        for _ in py2_xrange(spans):
            first = last + 1 + r.integer()
            last = first + (r.integer() if mode == b"R" else 0)
            if last >= volume:
                raise ValueError("index")
            for index in py2_xrange(first, last + 1):
                if index in used:
                    raise ValueError("overlap")
                used.add(index)
                indices.append(index)
    if r.offset != len(raw):
        raise ValueError("trailing bytes")
    return size, anchor, facing, groups
