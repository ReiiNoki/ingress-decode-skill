#!/usr/bin/env python3
"""
quick_decode.py — Ingress Passcode 解码快速工具箱

提供 Atbash、ROT、Base 系列、Morse、键盘偏移、方阵重排、盲文等常见解码算法。
核心功能 scan_all() 会运行与字符特征匹配的基础变换，帮助缩小范围。

用法:
    python scripts/quick_decode.py                     # 运行内置示例
    python scripts/quick_decode.py <密文字符串>        # 快速扫描一段密文

依赖: 仅标准库，无第三方依赖。
"""

from __future__ import annotations

import base64
import binascii
import re
import sys
from typing import Optional


HISTORICAL_PASSCODE_PATTERNS = {
    "investigation_2016": re.compile(
        r"^(?P<prefix>[A-Za-z]{3})(?P<n1>[2-9]{2})(?P<keyword>[A-Za-z]+)"
        r"(?P<n2>[2-9]{3})(?P<suffix>[A-Za-z]{2})$"
    ),
    "wotd_2016": re.compile(
        r"^(?P<a>[A-Za-z])(?P<n1>\d)(?P<b>[A-Za-z])(?P<n2>\d)"
        r"(?P<keyword>[A-Za-z]+)(?P<c>[A-Za-z])(?P<n3>\d)(?P<suffix>[A-Za-z]{2})$"
    ),
    "ingress_report_forever": re.compile(
        r"^(?P<keyword>[A-Za-z]+)(?P<n1>\d)(?P<a>[A-Za-z]{2})"
        r"(?P<n2>\d{2})(?P<b>[A-Za-z]{2})(?P<n3>\d)$"
    ),
    "anomaly_2016": re.compile(
        r"^(?P<prefix>[A-Za-z]{8})(?P<n1>[2-9])(?P<keyword>[A-Za-z]+)(?P<n2>[2-9])$"
    ),
    "old_2016": re.compile(
        r"^(?P<n1>[2-9])(?P<prefix>[A-Za-z]{3})(?P<n2>[2-9])"
        r"(?P<keyword>[A-Za-z]+)(?P<a>[A-Za-z])(?P<n3>[2-9])"
        r"(?P<b>[A-Za-z])(?P<n4>[2-9])(?P<c>[A-Za-z])$"
    ),
}


# ═══════════════════════════════════════════════
#  1. 基础变换
# ═══════════════════════════════════════════════

def reverse(s: str) -> str:
    """反转字符串"""
    return s[::-1]


def atbash(s: str, flip_digits: bool = False) -> str:
    """Atbash 字母翻转（26 字母前后对折）

    参数:
        s: 输入字符串
        flip_digits: 是否同时翻转数字 (0↔9, 1↔8, ...)

    示例:
        >>> atbash("cbt33nzplgl878iw")
        'xyg33makoto878rd'
    """
    t = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA"
    )
    result = s.translate(t)
    if flip_digits:
        t_d = str.maketrans("0123456789", "9876543210")
        result = result.translate(t_d)
    return result


def hex_atbash(s: str) -> str:
    """Hex Atbash：对 0-9a-f 做前后对折 (0↔f, 1↔e, ..., 7↔8)"""
    t = str.maketrans(
        "0123456789abcdefABCDEF",
        "fedcba9876543210FEDCBA",
    )
    return s.translate(t)


# ═══════════════════════════════════════════════
#  2. ROT / Caesar 系列
# ═══════════════════════════════════════════════

def rot(s: str, n: int = 13) -> str:
    """通用 ROT-n 字母移位"""
    result = []
    for ch in s:
        if "a" <= ch <= "z":
            result.append(chr((ord(ch) - ord("a") + n) % 26 + ord("a")))
        elif "A" <= ch <= "Z":
            result.append(chr((ord(ch) - ord("A") + n) % 26 + ord("A")))
        else:
            result.append(ch)
    return "".join(result)


def rot13(s: str) -> str:
    """ROT13（自逆）"""
    return rot(s, 13)


def rot5(s: str) -> str:
    """ROT5：数字移位，0↔5, 1↔6, ... 4↔9"""
    t = str.maketrans("0123456789", "5678901234")
    return s.translate(t)


def rot13_with_digits(s: str) -> str:
    """字母 ROT13 + 数字 ROT5 同时做"""
    return rot5(rot13(s))


def rot47(s: str) -> str:
    """ROT47：可打印 ASCII (33-126) 全范围移位"""
    result = []
    for ch in s:
        o = ord(ch)
        if 33 <= o <= 126:
            result.append(chr(33 + (o - 33 + 47) % 94))
        else:
            result.append(ch)
    return "".join(result)


def gronsfeld(s: str, numeric_key: str, decrypt: bool = True) -> str:
    """Gronsfeld 变换，用循环数字密钥对字母执行逐位 Caesar 移位。

    非字母不消耗密钥位。解密默认向后移；设置 ``decrypt=False`` 可加密。
    """
    digits = [int(ch) for ch in numeric_key if ch.isdigit()]
    if not digits:
        raise ValueError("numeric_key must contain at least one digit")
    result = []
    key_index = 0
    direction = -1 if decrypt else 1
    for ch in s:
        if ch.isascii() and ch.isalpha():
            result.append(rot(ch, direction * digits[key_index % len(digits)]))
            key_index += 1
        else:
            result.append(ch)
    return "".join(result)


def vigenere(s: str, key: str, decrypt: bool = True) -> str:
    """标准 Vigenere；非字母不消耗 key，大小写随输入保留。"""
    shifts = [ord(ch.lower()) - ord("a") for ch in key if ch.isascii() and ch.isalpha()]
    if not shifts:
        raise ValueError("key must contain at least one ASCII letter")
    result = []
    key_index = 0
    direction = -1 if decrypt else 1
    for ch in s:
        if ch.isascii() and ch.isalpha():
            result.append(rot(ch, direction * shifts[key_index % len(shifts)]))
            key_index += 1
        else:
            result.append(ch)
    return "".join(result)


def autokey_plaintext(s: str, key: str, decrypt: bool = True) -> str:
    """明文 AutoKey；密钥流为 keyword 后接明文，非字母不消耗 key。"""
    seed = [ord(ch.lower()) - ord("a") for ch in key if ch.isascii() and ch.isalpha()]
    if not seed:
        raise ValueError("key must contain at least one ASCII letter")
    stream = list(seed)
    result = []
    key_index = 0
    for ch in s:
        if not (ch.isascii() and ch.isalpha()):
            result.append(ch)
            continue
        shift = stream[key_index]
        value = ord(ch.lower()) - ord("a")
        plain_value = (value - shift) % 26 if decrypt else value
        output_value = plain_value if decrypt else (value + shift) % 26
        output = chr(ord("a") + output_value)
        result.append(output.upper() if ch.isupper() else output)
        stream.append(plain_value if decrypt else value)
        key_index += 1
    return "".join(result)


# ═══════════════════════════════════════════════
#  3. 编码 / 解码
# ═══════════════════════════════════════════════

def decode_base64(s: str, try_pad: bool = True) -> Optional[str]:
    """Base64 解码

    参数:
        s: 编码字符串
        try_pad: 是否自动补全 '=' 填充

    返回:
        解码后的字符串，失败返回 None
    """
    try:
        compact = re.sub(r"\s+", "", s)
        if try_pad:
            compact += "=" * ((4 - len(compact) % 4) % 4)
        raw = base64.b64decode(compact, validate=True)
        return raw.decode("utf-8")
    except Exception:
        return None


def decode_base32(s: str, try_pad: bool = True) -> Optional[str]:
    """Base32 解码；自动忽略空白并可补齐 ``=``。"""
    try:
        compact = re.sub(r"\s+", "", s).upper()
        if try_pad:
            compact += "=" * ((8 - len(compact) % 8) % 8)
        return base64.b32decode(compact, casefold=True).decode("utf-8")
    except Exception:
        return None


def decode_base85(s: str, adobe: bool = False) -> Optional[str]:
    """解码 RFC 1924 Base85；``adobe=True`` 时尝试 Ascii85。"""
    try:
        compact = re.sub(r"\s+", "", s).encode("ascii")
        raw = base64.a85decode(compact, adobe=adobe) if adobe else base64.b85decode(compact)
        return raw.decode("utf-8")
    except Exception:
        return None


def decode_uu_line(s: str) -> Optional[str]:
    """解码单行 uuencode 数据；多行文件应先保留原始换行逐行处理。"""
    try:
        return binascii.a2b_uu(s.encode("ascii")).decode("utf-8")
    except Exception:
        return None


def xor_hex_with_text(hex_text: str, key: str) -> Optional[str]:
    """将十六进制字节与循环文本 key 按位异或。"""
    try:
        data = bytes.fromhex(re.sub(r"\s+", "", hex_text))
        key_bytes = key.encode("utf-8")
        if not key_bytes:
            return None
        raw = bytes(value ^ key_bytes[i % len(key_bytes)] for i, value in enumerate(data))
        return raw.decode("utf-8")
    except Exception:
        return None


def decode_hex(s: str, sep: str = "") -> Optional[str]:
    """Hex 解码

    参数:
        s: 十六进制字符串，如 "48656c6c6f"
        sep: 分隔符，如 " " 或 "\\x"
    """
    try:
        raw = s.replace(sep, "").strip() if sep else s.strip()
        return bytes.fromhex(raw).decode("utf-8", errors="replace")
    except Exception:
        return None


def decode_binary(s: str, sep: str = " ") -> Optional[str]:
    """Binary 解码

    参数:
        s: 二进制字符串，如 "01001000 01101001"
        sep: 分隔符，传空则每 8 位切分
    """
    try:
        raw = s.strip()
        if not sep:
            raw = " ".join(raw[i:i+8] for i in range(0, len(raw), 8))
            sep = " "
        chars = [chr(int(b, 2)) for b in raw.split(sep) if b]
        return "".join(chars)
    except Exception:
        return None


def decode_ascii_decimal(s: str, sep: str = " ") -> Optional[str]:
    """ASCII decimal 解码

    参数:
        s: 十进制 ASCII 序列，如 "72 105"
    """
    try:
        chars = [chr(int(n)) for n in s.split(sep) if n.strip()]
        return "".join(chars)
    except Exception:
        return None


def a1z26(s: str, sep: str = " ") -> str:
    """A1Z26：数字转字母 (1=A, 2=B ... 26=Z)

    示例:
        >>> a1z26("1 26 6")
        'azf'
    """
    result = []
    for token in s.split(sep):
        token = token.strip()
        if token.isdigit():
            n = int(token)
            if 1 <= n <= 26:
                result.append(chr(ord("a") + n - 1))
            else:
                result.append(token)
        else:
            result.append(token)
    return "".join(result)


# ═══════════════════════════════════════════════
#  4. Morse 电码
# ═══════════════════════════════════════════════

MORSE_TABLE = {
    "A": ".-",     "B": "-...",   "C": "-.-.",
    "D": "-..",    "E": ".",      "F": "..-.",
    "G": "--.",    "H": "....",   "I": "..",
    "J": ".---",   "K": "-.-",    "L": ".-..",
    "M": "--",     "N": "-.",     "O": "---",
    "P": ".--.",   "Q": "--.-",   "R": ".-.",
    "S": "...",    "T": "-",      "U": "..-",
    "V": "...-",   "W": ".--",    "X": "-..-",
    "Y": "-.--",   "Z": "--..",
    "0": "-----",  "1": ".----",  "2": "..---",
    "3": "...--",  "4": "....-",  "5": ".....",
    "6": "-....",  "7": "--...",  "8": "---..",
    "9": "----.",
}

MORSE_REVERSE = {v: k for k, v in MORSE_TABLE.items()}


def decode_morse(s: str, dot: str = ".", dash: str = "-",
                 char_sep: str = " ", word_sep: str = " / ") -> str:
    """Morse 电码解码

    参数:
        s: 摩斯字符串
        dot: 点的符号（默认 "."，类 Morse 可替换）
        dash: 划的符号（默认 "-"）

    示例:
        >>> decode_morse("-- / .... / -")
        'MHT'
    """
    if dot == dash:
        raise ValueError("dot and dash must be different symbols")
    placeholders = {dot: "\x00", dash: "\x01"}
    for source, target in placeholders.items():
        s = s.replace(source, target)
    s = s.replace("\x00", ".").replace("\x01", "-")
    result = []
    for word in s.split(word_sep):
        for code in word.split(char_sep):
            code = code.strip()
            if code:
                result.append(MORSE_REVERSE.get(code, "?"))
        result.append(" ")
    return "".join(result).strip()


def encode_morse(s: str, char_sep: str = " ", word_sep: str = " / ") -> str:
    """文本转 Morse 电码"""
    words = s.upper().split()
    encoded = []
    for word in words:
        codes = [MORSE_TABLE.get(ch, "?") for ch in word]
        encoded.append(char_sep.join(codes))
    return word_sep.join(encoded)


def keyboard_row_to_morse(s: str) -> str:
    """键盘三行转摩斯：顶行=划, 中行=点, 底行=分隔符

    QWERTY 布局:
      顶行 q w e r t y u i o p  → "―" (dash)
      中行 a s d f g h j k l    → "·" (dot)
      底行 z x c v b n m        → "/" (word sep)

    示例:
        >>> keyboard_row_to_morse("lfcreebruahcsq")
        '-- / .... / - / ..--- / --'
    """
    top = set("qwertyuiop")
    mid = set("asdfghjkl")
    bot = set("zxcvbnm")
    result = []
    for ch in s.lower():
        if ch in top:
            result.append("-")
        elif ch in mid:
            result.append(".")
        elif ch in bot:
            result.append(" / ")
    return "".join(result)


# ═══════════════════════════════════════════════
#  5. 键盘偏移
# ═══════════════════════════════════════════════

QWERTY_LAYER = [
    "1234567890",
    "qwertyuiop",
    "asdfghjkl;",
    "zxcvbnm,./",
]

QWERTY_SHIFTED_LAYER = [
    "!@#$%^&*()",
    "QWERTYUIOP",
    "ASDFGHJKL:",
    "ZXCVBNM<>?",
]

def _build_keyboard_map(shift: int = 1, mirror: bool = False):
    """生成键盘映射表"""
    mapping = {}
    for row in QWERTY_LAYER + QWERTY_SHIFTED_LAYER:
        n = len(row)
        for i, ch in enumerate(row):
            if mirror:
                target = row[n - 1 - i]
            else:
                target_index = i + shift
                target = row[target_index] if 0 <= target_index < n else ch
            mapping[ch] = target
            mapping[ch.upper()] = target.upper()
    return mapping


def keyboard_shift(s: str, direction: str = "left") -> str:
    """QWERTY 键盘移位

    参数:
        s: 输入字符
        direction: "left" / "right" / "mirror"

    示例:
        >>> keyboard_shift("y d", "left")
        't s'
    """
    shift_map = {
        "left": _build_keyboard_map(-1),
        "right": _build_keyboard_map(1),
        "mirror": _build_keyboard_map(mirror=True),
    }
    m = shift_map.get(direction, shift_map["left"])
    return "".join(m.get(ch, ch) for ch in s)


# ═══════════════════════════════════════════════
#  6. 方阵 / 矩阵重排
# ═══════════════════════════════════════════════

def rect(s: str, cols: int) -> list[str]:
    """按指定列数排成矩阵（行优先），返回每行字符串的列表"""
    return [s[i:i+cols] for i in range(0, len(s), cols)]


def read_columns(s: str, cols: int) -> str:
    """按列读取（从上往下，从左往右）"""
    rows = rect(s, cols)
    return "".join(r[c] for c in range(cols) for r in rows if c < len(r))


def read_columns_reverse(s: str, cols: int) -> str:
    """按列从下往上读取"""
    rows = rect(s, cols)
    return "".join(r[c] for c in range(cols) for r in reversed(rows) if c < len(r))


def read_rows_bottom_up(s: str, cols: int) -> str:
    """从最底行开始往上逐行读取"""
    return "".join(reversed(rect(s, cols)))


def rotate_90(s: str, cols: int) -> str:
    """矩阵顺时针旋转 90 度后按行读取"""
    rows = rect(s, cols)
    result = []
    for c in range(cols):
        for r in reversed(rows):
            if c < len(r):
                result.append(r[c])
    return "".join(result)


def try_all_rect(s: str) -> dict[str, str]:
    """尝试所有可能的矩阵读法，返回结果字典"""
    results = {}
    # 找所有因数作为可能的列数
    n = len(s)
    col_candidates = [c for c in range(2, n) if n % c == 0]
    if not col_candidates:
        col_candidates = [c for c in range(2, min(n, 10))]

    for cols in col_candidates:
        tag = f"rect({cols})"
        results[f"{tag}_rows_bottom_up"] = read_rows_bottom_up(s, cols)
        results[f"{tag}_columns"] = read_columns(s, cols)
        results[f"{tag}_columns_rev"] = read_columns_reverse(s, cols)
        results[f"{tag}_rotate90"] = rotate_90(s, cols)
    return results


# ═══════════════════════════════════════════════
#  7. 栅栏密码 (Rail Fence)
# ═══════════════════════════════════════════════

def decode_rail_fence(s: str, rails: int) -> str:
    """栅栏/篱笆密码解码"""
    n = len(s)
    fence = [[""] * n for _ in range(rails)]
    r, dr = 0, 1
    for c in range(n):
        fence[r][c] = "*"
        if r == 0:
            dr = 1
        elif r == rails - 1:
            dr = -1
        r += dr
    idx = 0
    for r in range(rails):
        for c in range(n):
            if fence[r][c] == "*":
                fence[r][c] = s[idx]
                idx += 1
    r, dr = 0, 1
    result = []
    for c in range(n):
        result.append(fence[r][c])
        if r == 0:
            dr = 1
        elif r == rails - 1:
            dr = -1
        r += dr
    return "".join(result)


# ═══════════════════════════════════════════════
#  8. 盲文辅助
# ═══════════════════════════════════════════════

# 标准英文盲文（Unicode 盲文字符 → 拉丁字母）
BRAILLE_TO_LATIN: dict[str, str] = {
    "⠁": "a", "⠃": "b", "⠉": "c", "⠙": "d", "⠑": "e",
    "⠋": "f", "⠛": "g", "⠓": "h", "⠊": "i", "⠚": "j",
    "⠅": "k", "⠇": "l", "⠍": "m", "⠝": "n", "⠕": "o",
    "⠏": "p", "⠟": "q", "⠗": "r", "⠎": "s", "⠞": "t",
    "⠥": "u", "⠧": "v", "⠺": "w", "⠭": "x", "⠽": "y",
    "⠵": "z",
}


def braille_to_text(s: str) -> str:
    """Braille Unicode 转拉丁字母"""
    return "".join(BRAILLE_TO_LATIN.get(ch, ch) for ch in s)


def braille_dot_count(ch: str) -> int:
    """计算盲文字符的点数"""
    return bin(ord(ch) & 0x3F).count("1")


def braille_multiply_dots(text: str, group: int = 2) -> list[int]:
    """盲文点数相乘取个位

    参数:
        text: 盲文 Unicode 字符串
        group: 每几个字符一组相乘

    示例:
        >>> braille_multiply_dots("⠎⠊⠑⠊")  # S I E I
        [6, 4]
    """
    counts = [braille_dot_count(ch) for ch in text]
    result = []
    for i in range(0, len(counts), group):
        product = 1
        for j in range(group):
            if i + j < len(counts):
                product *= counts[i + j]
        result.append(product % 10)
    return result


# ═══════════════════════════════════════════════
#  9. 其他编码
# ═══════════════════════════════════════════════

MULTITAP = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}


def decode_multitap_pairs(s: str, order: str = "press-key") -> Optional[str]:
    """解码两位一组的电话键盘码。

    ``press-key`` 表示第一位是按键次数、第二位是键号，和归档文章 No.99、
    No.145、No.408 的写法一致；``key-press`` 表示相反顺序。
    """
    digits = re.sub(r"\D", "", s)
    if len(digits) % 2:
        return None
    output = []
    for i in range(0, len(digits), 2):
        first, second = digits[i], digits[i + 1]
        presses, key = (first, second) if order == "press-key" else (second, first)
        letters = MULTITAP.get(key)
        if not letters or not presses.isdigit() or not 1 <= int(presses) <= len(letters):
            return None
        output.append(letters[int(presses) - 1])
    return "".join(output)


def decode_multitap_runs(s: str) -> Optional[str]:
    """解码 ``777 666 8`` 这类重复按键式 multi-tap。"""
    groups = re.findall(r"([2-9])\1*", re.sub(r"[\s-]+", "", s))
    compact = re.sub(r"[\s-]+", "", s)
    if not groups or sum(len(match.group(0)) for match in re.finditer(r"([2-9])\1*", compact)) != len(compact):
        return None
    output = []
    for match in re.finditer(r"([2-9])\1*", compact):
        key = match.group(1)
        run = len(match.group(0))
        letters = MULTITAP[key]
        if run > len(letters):
            return None
        output.append(letters[run - 1])
    return "".join(output)


def decode_alternating_run_lengths(counts: str, start_bit: str = "0") -> Optional[str]:
    """把一串十进制位解释为 0/1 交替游程长度，并按 8 位 ASCII 解码。"""
    compact = re.sub(r"\s+", "", counts)
    if not compact.isdigit() or start_bit not in {"0", "1"}:
        return None
    bit = start_bit
    bits = []
    for ch in compact:
        bits.append(bit * int(ch))
        bit = "1" if bit == "0" else "0"
    binary = "".join(bits)
    if not binary or len(binary) % 8:
        return None
    return decode_binary(binary, sep="")

def leet_decode(s: str) -> str:
    """简单 Leetspeak 转字母（仅处理最常见替换）"""
    leet_map = {
        "0": "o", "1": "l", "2": "z", "3": "e", "4": "a",
        "5": "s", "6": "g", "7": "t", "8": "b", "9": "g",
        "@": "a", "$": "s", "!": "i",
    }
    return "".join(leet_map.get(ch, ch) for ch in s)


def decode_url_encoded(s: str) -> Optional[str]:
    """URL 编码解码 (%XX)"""
    try:
        from urllib.parse import unquote
        return unquote(s)
    except Exception:
        return None


def character_profile(s: str) -> dict[str, object]:
    """返回解题前最有用的长度、字符类别和矩阵因数信息。"""
    compact = re.sub(r"\s+", "", s)
    factors = [n for n in range(2, len(compact)) if len(compact) % n == 0]

    def kind(ch: str) -> str:
        if ch.islower():
            return "a"
        if ch.isupper():
            return "A"
        if ch.isdigit():
            return "9"
        if ch.isspace():
            return "_"
        return "!"

    pattern = "".join(kind(ch) for ch in s)
    collapsed = re.sub(r"(.)\1+", r"\1", pattern)
    return {
        "length": len(s),
        "compact_length": len(compact),
        "unique_characters": len(set(compact)),
        "lowercase": sum(ch.islower() for ch in s),
        "uppercase": sum(ch.isupper() for ch in s),
        "digits": sum(ch.isdigit() for ch in s),
        "symbols": sum(not ch.isalnum() and not ch.isspace() for ch in s),
        "class_pattern": pattern,
        "class_runs": collapsed,
        "factors": factors,
    }


def match_historical_passcode(s: str) -> list[dict[str, object]]:
    """匹配 2016 归档记录的格式；结果只是历史格式提示，不证明答案正确。"""
    compact = re.sub(r"\s+", "", s)
    matches = []
    for source, pattern in HISTORICAL_PASSCODE_PATTERNS.items():
        match = pattern.fullmatch(compact)
        if match:
            matches.append({"source": source, "parts": match.groupdict()})
    return matches


# ═══════════════════════════════════════════════
#  10. 识别与辅助
# ═══════════════════════════════════════════════

def guess_encoding(s: str) -> list[str]:
    """猜测密文可能的编码类型，返回建议列表"""
    hints = []
    compact = re.sub(r"\s+", "", s)
    n = len(compact)
    if re.fullmatch(r"[0-9\s]+", s):
        hints.append("A1Z26 / ASCII decimal / 坐标 / 元素序号")
    if re.fullmatch(r"[01\s]+", s):
        hints.append("Binary / Braille / 培根密码")
    if re.fullmatch(r"[.\-\s/]+", s):
        hints.append("Morse 或类 Morse")
    if re.fullmatch(r"[A-Za-z0-9+/=]+", compact) and n >= 8 and n % 4 in {0, 2, 3}:
        hints.append("Base64")
    if re.fullmatch(r"[A-Z2-7=]+", compact, re.IGNORECASE) and n >= 8:
        hints.append("Base32")
    if re.fullmatch(r"[0-9a-fA-F\s]+", s):
        hints.append("Hex")
    if re.search(r"[\u2800-\u28FF]", s):
        hints.append("Braille（盲文）")
    if "%" in s:
        hints.append("URL encoded")
    if re.fullmatch(r"[A-Za-z]+", s):
        hints.append("Atbash / ROT / Reverse / 替换")
    if re.fullmatch(r"[A-Za-z0-9]+", s):
        hints.append("可能有 passcode 格式特征")
    if not hints:
        hints.append("检查是否含图片、文件名、标题等外部线索")
    return hints


# ═══════════════════════════════════════════════
#  11. 快速全扫描
# ═══════════════════════════════════════════════

def scan_all(s: str) -> dict[str, str]:
    """一键扫描所有基础变换，快速缩小范围

    参数:
        s: 待扫描的密文字符串

    返回:
        算法名称 → 结果的字典

    示例:
        >>> import json; r = scan_all("cbt33nzplgl878iw")
        >>> print(json.dumps(r, indent=2))
    """
    result: dict[str, str] = {}

    # 基础变换
    result["reverse"] = reverse(s)
    result["atbash"] = atbash(s)
    result["hex_atbash"] = hex_atbash(s)

    # ROT 系列
    result["rot13"] = rot13(s)
    result["rot5"] = rot5(s)
    result["rot13+rot5"] = rot13_with_digits(s)
    result["rot47"] = rot47(s)

    # 键盘偏移
    result["keyboard_left"] = keyboard_shift(s, "left")
    result["keyboard_right"] = keyboard_shift(s, "right")
    result["keyboard_mirror"] = keyboard_shift(s, "mirror")

    compact = re.sub(r"\s+", "", s)

    # Base family
    b64 = decode_base64(s)
    if b64:
        result["base64"] = b64
    b32 = decode_base32(s)
    if b32:
        result["base32"] = b32
    b85 = decode_base85(s)
    if b85:
        result["base85"] = b85

    # Numeric and symbol encodings. Only add successful, printable results.
    if re.fullmatch(r"[0-9a-fA-F\s]+", s) and len(re.sub(r"\s+", "", s)) % 2 == 0:
        decoded = decode_hex(s)
        if decoded and decoded.isprintable():
            result["hex"] = decoded
    if re.fullmatch(r"[01\s]+", s):
        decoded = decode_binary(s, sep="" if " " not in s.strip() else " ")
        if decoded and decoded.isprintable():
            result["binary"] = decoded
    if re.fullmatch(r"(?:\d{2,3}[\s,;:/-]*)+", s):
        tokens = re.findall(r"\d{2,3}", s)
        decoded = decode_ascii_decimal(" ".join(tokens))
        if decoded and decoded.isprintable():
            result["ascii_decimal"] = decoded
    numeric_tokens = re.findall(r"\d+", s)
    if numeric_tokens and re.fullmatch(r"[\d\s,;:/-]+", s):
        if all(1 <= int(token) <= 26 for token in numeric_tokens):
            result["a1z26"] = a1z26(" ".join(numeric_tokens))
    if re.fullmatch(r"[.\-/\s]+", s):
        result["morse"] = decode_morse(s)
        result["morse_swapped"] = decode_morse(s, dot="-", dash=".")
    if re.fullmatch(r"(?:[1-4][2-9][\s-]*)+", s):
        for order in ("press-key", "key-press"):
            decoded = decode_multitap_pairs(s, order)
            if decoded:
                result[f"multitap_{order}"] = decoded
    if re.fullmatch(r"(?:([2-9])\1*[\s-]*)+", s):
        decoded = decode_multitap_runs(s)
        if decoded:
            result["multitap_runs"] = decoded
    if compact.isdigit() and sum(int(ch) for ch in compact) % 8 == 0:
        for start_bit in ("0", "1"):
            decoded = decode_alternating_run_lengths(compact, start_bit)
            if decoded and decoded.isprintable():
                result[f"rle_start_{start_bit}"] = decoded

    # URL and leetspeak are cheap and preserve useful evidence.
    if "%" in s:
        decoded = decode_url_encoded(s)
        if decoded and decoded != s:
            result["url_decode"] = decoded
    leet = leet_decode(s)
    if leet != s:
        result["leetspeak"] = leet

    # 矩阵尝试（只取前几种，避免输出过多）
    rect_results = try_all_rect(s)
    for k, v in list(rect_results.items())[:8]:
        result[k] = v

    # 猜测编码类型
    guesses = guess_encoding(s)
    profile = character_profile(s)
    format_matches = match_historical_passcode(s)
    if format_matches:
        result["historical_format"] = ", ".join(
            f"{match['source']} keyword={match['parts'].get('keyword')}"
            for match in format_matches
        )
    print(
        f"[字符概况] 长度={profile['length']} 去空白={profile['compact_length']} "
        f"数字={profile['digits']} 符号={profile['symbols']} 因数={profile['factors']}",
        file=sys.stderr,
    )
    print(f"[建议优先尝试] {' / '.join(guesses)}", file=sys.stderr)

    return result


# ═══════════════════════════════════════════════
#  命令行入口
# ═══════════════════════════════════════════════

def main():
    if len(sys.argv) > 1:
        # 用户提供密文，一键扫描
        raw = " ".join(sys.argv[1:])
        print(f"密文: {raw}")
        print("=" * 50)
        results = scan_all(raw)
        for k, v in results.items():
            label = k.replace("_", " ").title()
            print(f"  {label:25s} → {v}")
    else:
        # 运行内置示例
        print("=" * 60)
        print("Ingress Passcode Decode — 快速解码工具箱")
        print("用法: python quick_decode.py <密文字符串>")
        print("=" * 60)

        print("\n=== 案例 1: Atbash ===")
        print(f"  密文: cbt33nzplgl878iw")
        print(f"  结果: {atbash('cbt33nzplgl878iw')}")

        print("\n=== 案例 2: 键盘手滑 (Reverse + ROT-5) ===")
        raw = "yd623qfztu63bhw"
        r1 = reverse(raw)
        r2 = rot(r1, -5)
        print(f"  原始:     {raw}")
        print(f"  Reverse:  {r1}")
        print(f"  ROT-5:    {r2}")
        print(f"  修正typo: {r2.replace('poual', 'portal')}  ← poual → portal")

        print("\n=== 案例 3: 盲文 ===")
        b = "⠃⠧⠑⠎⠊⠑⠊⠎⠉⠊⠑⠝⠉⠑⠞⠺⠑⠊⠋⠕⠁⠎"
        letters = braille_to_text(b)
        print(f"  盲文:   {b}")
        print(f"  字母:   {letters}")
        print(f"  Keyword: SCIENCE → 查看 references/examples.md 完整链路")

        print("\n=== 案例 4: rect(4) 矩阵 ===")
        s = "37koati52azmwoq3"
        print(f"  密文:           {s}")
        print(f"  左下→右上逐行:   {read_rows_bottom_up(s, 4)}")

        print("\n=== 案例 5: 键盘行→Morse (完整链路见 examples.md) ===")
        # 简化示例，演示函数用法
        test = "qaz"  # q(顶行→-) a(中行→.) z(底行→/)
        morse = keyboard_row_to_morse(test)
        print(f"  keyboard_row_to_morse('qaz') → '{morse}'")
        print(f"  完整案例见 references/examples.md")

        print("\n=== 案例 6: 一键扫描 ===")
        scan = scan_all("cbt33nzplgl878iw")
        for k, v in scan.items():
            print(f"  {k:25s} → {v}")


if __name__ == "__main__":
    main()
