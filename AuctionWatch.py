#!/usr/bin/env python3
"""
AuctionWatch -- standalone FFXI item & Auction-House browser.

Search FFXI items by name, see their description / category / stack size, and
pull live Auction House sales history straight from your world's search server
(no game running required -- the search server answers unauthenticated).

Needs `ffxi_items.json` (the bundled item database) next to this file, or
bundled into the exe. Pure standard library + tkinter -- no pip installs.
"""
import base64
import hashlib
import socket
import os
import sys
import subprocess
import time
import json
import gzip
import re
import math
import threading
import datetime
import statistics
import webbrowser
import collections as _collections
import tkinter as tk
from tkinter import ttk

_DEFAULT_SERVER = "124.150.154.63"

import struct as _ahsrch_struct
import hashlib as _ahsrch_hashlib

_AHSRCH_PORT = 54002
_AHSRCH_MASK = 0xFFFFFFFF
_AHSRCH_KEY_SEED = bytes((0x30, 0x73, 0x3D, 0x6D, 0x3C, 0x31, 0x49, 0x5A,
                          0x32, 0x7A, 0x42, 0x43, 0x63, 0x38, 0x7B, 0x7E))
_AHSRCH_IXFF = 0x46465849
_AHSRCH_HIST_SINGLE = 0x05
_AHSRCH_HIST_STACK = 0x06
_AHSRCH_SUBKEY = base64.b64decode(
    "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"
    "349X5nLDOg=="
)


def _ahsrch_load_ps():
    P = list(_ahsrch_struct.unpack("<18I", _AHSRCH_SUBKEY[0:72]))
    S = list(_ahsrch_struct.unpack("<1024I", _AHSRCH_SUBKEY[72:72 + 4096]))
    return P, S


def _ahsrch_TT(x, S):
    return ((((S[256 + ((x >> 8) & 0xFF)] & 1) ^ 32)
             + ((S[768 + ((x >> 24) & 0xFF)] & 1) ^ 32)
             + S[512 + ((x >> 16) & 0xFF)]
             + S[x & 0xFF]) & _AHSRCH_MASK)


def _ahsrch_encipher(xl, xr, P, S):
    for i in range(16):
        xl = (xl ^ P[i]) & _AHSRCH_MASK
        xr = (_ahsrch_TT(xl, S) ^ xr) & _AHSRCH_MASK
        xl, xr = xr, xl
    xl, xr = xr, xl
    xr = (xr ^ P[16]) & _AHSRCH_MASK
    xl = (xl ^ P[17]) & _AHSRCH_MASK
    return xl, xr


def _ahsrch_decipher(xl, xr, P, S):
    for i in range(17, 1, -1):
        xl = (xl ^ P[i]) & _AHSRCH_MASK
        xr = (_ahsrch_TT(xl, S) ^ xr) & _AHSRCH_MASK
        xl, xr = xr, xl
    xl, xr = xr, xl
    xr = (xr ^ P[1]) & _AHSRCH_MASK
    xl = (xl ^ P[0]) & _AHSRCH_MASK
    return xl, xr


def _ahsrch_blowfish_init(key_bytes):
    # The server treats the key as SIGNED int8, so digest bytes >= 0x80
    # sign-extend when folded into the P-array. Replicate exactly.
    P, S = _ahsrch_load_ps()
    n = len(key_bytes)
    j = 0
    for i in range(18):
        data = 0
        for _ in range(4):
            b = key_bytes[j]
            sb = b - 256 if b >= 128 else b
            data = ((data << 8) | (sb & _AHSRCH_MASK)) & _AHSRCH_MASK
            j += 1
            if j >= n:
                j = 0
        P[i] = (P[i] ^ data) & _AHSRCH_MASK
    dl, dr = 0, 0
    for i in range(0, 18, 2):
        dl, dr = _ahsrch_encipher(dl, dr, P, S)
        P[i], P[i + 1] = dl, dr
    for i in range(4):
        for k in range(0, 256, 2):
            dl, dr = _ahsrch_encipher(dl, dr, P, S)
            S[i * 256 + k], S[i * 256 + k + 1] = dl, dr
    return P, S


def _ahsrch_cipher_blocks(buf, length, P, S, decrypt):
    tmp = (length - 12) // 4
    tmp -= tmp % 2
    i = 0
    while i < tmp:
        o = 8 + i * 4
        xl, xr = _ahsrch_struct.unpack_from("<II", buf, o)
        xl, xr = (_ahsrch_decipher if decrypt else _ahsrch_encipher)(xl, xr, P, S)
        _ahsrch_struct.pack_into("<II", buf, o, xl, xr)
        i += 2


def _ahsrch_md5(b):
    return _ahsrch_hashlib.md5(b).digest()


def _ahsrch_build_request(item_id, stack=False, key_tail=None):
    # Matches the real retail client packet family (from a live capture): 76
    # bytes; size@0x00, IXFF@0x04, then [u16 size][0x80 flag][type] at 0x08.
    # The 0x80 flag byte at 0x0A is required — without it the server stays
    # silent. itemid@0x12, stack@0x15. md5 hash + key tail footer.
    if key_tail is None:
        key_tail = os.urandom(4)
    length = 76
    buf = bytearray(length)
    _ahsrch_struct.pack_into("<H", buf, 0x00, length)
    _ahsrch_struct.pack_into("<I", buf, 0x04, _AHSRCH_IXFF)
    _ahsrch_struct.pack_into("<H", buf, 0x08, 16)
    buf[0x0A] = 0x80
    buf[0x0B] = _AHSRCH_HIST_STACK if stack else _AHSRCH_HIST_SINGLE
    _ahsrch_struct.pack_into("<H", buf, 0x12, item_id & 0xFFFF)
    buf[0x15] = 1 if stack else 0
    buf[length - 0x14:length - 0x04] = _ahsrch_md5(bytes(buf[0x08:length - 0x14]))
    buf[length - 0x04:length] = key_tail
    P, S = _ahsrch_blowfish_init(_ahsrch_md5(_AHSRCH_KEY_SEED + key_tail))
    _ahsrch_cipher_blocks(buf, length, P, S, decrypt=False)
    return bytes(buf), key_tail


def _ahsrch_req_key20_24(item_id, stack):
    # We zero the key2 region (length-0x18) in the request, so the server
    # derives key2 = 0 for response encryption; mirror that here.
    return b"\x00\x00\x00\x00"


def _ahsrch_decode_name(raw):
    z = raw.find(b"\x00")
    if z >= 0:
        raw = raw[:z]
    return raw.decode("latin-1", "replace").strip()


def _ahsrch_parse_response(buf, key_tail, req_key20_24):
    buf = bytearray(buf)
    length = _ahsrch_struct.unpack_from("<H", buf, 0x00)[0]
    if length < 28 or length > len(buf):
        raise ValueError("bad response length %d (have %d bytes)" % (length, len(buf)))
    P, S = _ahsrch_blowfish_init(_ahsrch_md5(_AHSRCH_KEY_SEED + key_tail + req_key20_24))
    _ahsrch_cipher_blocks(buf, length, P, S, decrypt=True)
    item_id = _ahsrch_struct.unpack_from("<H", buf, 0x18)[0]
    amount = _ahsrch_struct.unpack_from("<I", buf, 0x1A)[0]
    category = _ahsrch_struct.unpack_from("<H", buf, 0x1E)[0]
    marker = _ahsrch_struct.unpack_from("<H", buf, 0x08)[0]
    n = max(0, (marker - 0x20) // 40)
    sales = []
    for i in range(n):
        o = 0x20 + 40 * i
        if o + 40 > length:
            break
        price = _ahsrch_struct.unpack_from("<I", buf, o + 0x00)[0]
        date = _ahsrch_struct.unpack_from("<I", buf, o + 0x04)[0]
        seller = _ahsrch_decode_name(bytes(buf[o + 0x08:o + 0x08 + 15]))
        buyer = _ahsrch_decode_name(bytes(buf[o + 0x18:o + 0x18 + 15]))
        sales.append({"price": price, "date": date, "seller": seller, "buyer": buyer})
    return {"item_id": item_id, "amount": amount, "category": category, "sales": sales}


class _AhsrchProto(Exception):
    def __init__(self, msg, data=b"", sent=0):
        self.data = data
        self.sent = sent
        super().__init__(msg)


def _ahsrch_query(host, port, item_id, stack=False, timeout=8.0):
    req, key_tail = _ahsrch_build_request(item_id, stack)
    key20_24 = _ahsrch_req_key20_24(item_id, stack)
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.sendall(req)
        s.settimeout(timeout)
        data = b""
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(data) >= 2 and len(data) >= _ahsrch_struct.unpack_from("<H", data, 0)[0]:
                    break
        except socket.timeout:
            pass
    if len(data) < 2 or len(data) < _ahsrch_struct.unpack_from("<H", data, 0)[0]:
        raise _AhsrchProto("short response", data, len(req))
    return _ahsrch_parse_response(data, key_tail, key20_24)


def _ahsrch_no_window_kw():
    # Keep netstat from flashing a console window on Windows.
    import subprocess
    kw = {}
    try:
        if os.name == "nt":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0  # SW_HIDE
            kw["startupinfo"] = si
            kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    except Exception:
        pass
    return kw


def _ahsrch_manual_server():
    """Optional manual override: %APPDATA%/OmniWatch/search_server.txt holding
    'ip' or 'ip:port'. Lets you point at a world's search server by hand if
    auto-detect can't find it. Returns (ip, port) or None."""
    try:
        path = os.path.join(os.environ.get("APPDATA", ""), "OmniWatch", "search_server.txt")
        with open(path, "r") as f:
            txt = f.read().strip()
        if not txt:
            return None
        if ":" in txt:
            ip, _, pp = txt.partition(":")
            return ip.strip(), int(pp.strip() or _AHSRCH_PORT)
        return txt, _AHSRCH_PORT
    except Exception:
        return None


def _ahsrch_cache_path():
    return os.path.join(os.environ.get("APPDATA", ""), "OmniWatch", "search_server_cache.txt")


def _ahsrch_load_cached():
    try:
        with open(_ahsrch_cache_path(), "r") as f:
            ip = f.read().strip()
        return ip or None
    except Exception:
        return None


def _ahsrch_save_cached(ip):
    try:
        path = _ahsrch_cache_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(ip)
    except Exception:
        pass


def _ahsrch_clear_cached():
    try:
        os.remove(_ahsrch_cache_path())
    except Exception:
        pass


def _ahsrch_find_server(port=_AHSRCH_PORT):
    """Auto-detect the current world's search server from this PC's TCP table.
    The FFXI client opens a connection to it on the search port when you /search
    (or browse the AH); we match any state, so a recent (TIME_WAIT) connection
    still counts. Returns IP or None."""
    import subprocess
    try:
        import psutil
        for c in psutil.net_connections(kind="tcp"):
            if (c.raddr and c.raddr.port == port
                    and c.raddr.ip not in ("0.0.0.0", "127.0.0.1")):
                return c.raddr.ip
    except Exception:
        pass
    out = ""
    for cmd in (["netstat", "-ano", "-p", "TCP"], ["netstat", "-an"]):
        try:
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL,
                                          **_ahsrch_no_window_kw())
            break
        except Exception:
            continue
    pat = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}):%d\b" % port)
    for line in out.splitlines():
        if ("LISTEN" in line.upper()) or ((":%d" % port) not in line):
            continue
        m = pat.search(line)
        if m and m.group(1) not in ("0.0.0.0", "127.0.0.1"):
            return m.group(1)
    return None


def _ahsrch_fmtdate(ts):
    try:
        return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
    except Exception:
        return str(ts)


def _ahsrch_build_category_request(cat, key2=b"\x00\x00\x00\x00", key_tail=None):
    # 0x15 AH category listing request, byte-for-byte matching the real retail
    # client packet (verified against a live capture): 268 bytes, category at
    # 0x16, one sort param (by level) at 0x18.
    if key_tail is None:
        key_tail = os.urandom(4)
    length = 268
    buf = bytearray(length)
    _ahsrch_struct.pack_into("<H", buf, 0x00, length)
    _ahsrch_struct.pack_into("<I", buf, 0x04, _AHSRCH_IXFF)
    _ahsrch_struct.pack_into("<H", buf, 0x08, 184)
    buf[0x0A] = 0x80
    buf[0x0B] = 0x15
    _ahsrch_struct.pack_into("<H", buf, 0x0E, 1)
    buf[0x12] = 1                       # paramCount
    _ahsrch_struct.pack_into("<H", buf, 0x14, 4)
    buf[0x16] = cat & 0xFF              # AHCatID
    _ahsrch_struct.pack_into("<I", buf, 0x18, 2)
    _ahsrch_struct.pack_into("<I", buf, 0x1C, 2)
    buf[length - 0x18:length - 0x14] = key2
    buf[length - 0x14:length - 0x04] = _ahsrch_md5(bytes(buf[0x08:length - 0x14]))
    buf[length - 0x04:length] = key_tail
    P, S = _ahsrch_blowfish_init(_ahsrch_md5(_AHSRCH_KEY_SEED + key_tail))
    _ahsrch_cipher_blocks(buf, length, P, S, decrypt=False)
    return bytes(buf)


def _ahsrch_build_more_request(key2=b"\x00\x00\x00\x00", key_tail=None):
    # 0x10 "next page" request (the server tracks the query state per
    # connection, so this just advances the current category listing).
    if key_tail is None:
        key_tail = os.urandom(4)
    length = 76
    buf = bytearray(length)
    _ahsrch_struct.pack_into("<H", buf, 0x00, length)
    _ahsrch_struct.pack_into("<I", buf, 0x04, _AHSRCH_IXFF)
    _ahsrch_struct.pack_into("<H", buf, 0x08, 16)
    buf[0x0A] = 0x80
    buf[0x0B] = 0x10
    _ahsrch_struct.pack_into("<H", buf, 0x10, 3)
    _ahsrch_struct.pack_into("<H", buf, 0x12, 1)
    buf[length - 0x18:length - 0x14] = key2
    buf[length - 0x14:length - 0x04] = _ahsrch_md5(bytes(buf[0x08:length - 0x14]))
    buf[length - 0x04:length] = key_tail
    P, S = _ahsrch_blowfish_init(_ahsrch_md5(_AHSRCH_KEY_SEED + key_tail))
    _ahsrch_cipher_blocks(buf, length, P, S, decrypt=False)
    return bytes(buf)


def _ahsrch_recv_packet(s, timeout):
    data = b""
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) >= 2 and len(data) >= _ahsrch_struct.unpack_from("<H", data, 0)[0]:
                break
    except socket.timeout:
        pass
    return data


def _ahsrch_parse_listing(data, key2):
    # Decrypt + parse one 0x95 AH listing page. Returns (items, total, is_last)
    # where items is {itemid: (single_count, stack_count)}; 0xFFFFFFFF means the
    # item has no listing of that form (e.g. doesn't stack). None on failure.
    if len(data) < 2:
        return None
    buf = bytearray(data)
    length = _ahsrch_struct.unpack_from("<H", buf, 0)[0]
    if length < 28 or length > len(buf):
        return None
    P, S = _ahsrch_blowfish_init(_ahsrch_md5(_AHSRCH_KEY_SEED + bytes(buf[length - 4:length]) + key2))
    _ahsrch_cipher_blocks(buf, length, P, S, decrypt=True)
    if buf[0x0B] != 0x95:
        return None
    total = _ahsrch_struct.unpack_from("<H", buf, 0x0E)[0]
    end = _ahsrch_struct.unpack_from("<H", buf, 0x08)[0]
    is_last = (buf[0x0A] == 0x80)
    items = {}
    n = max(0, (end - 0x18) // 10)
    for i in range(n):
        o = 0x18 + 10 * i
        if o + 10 > length:
            break
        iid = _ahsrch_struct.unpack_from("<H", buf, o)[0]
        single = _ahsrch_struct.unpack_from("<I", buf, o + 2)[0]
        stack = _ahsrch_struct.unpack_from("<I", buf, o + 6)[0]
        items[iid] = (single, stack)
    return items, total, is_last


def _ahsrch_query_category(host, port, cat, timeout=8.0):
    # Query one AH category: send 0x15, then page with 0x10 until the last-page
    # flag. Returns {"items": {itemid:(single,stack)}, "total": int}.
    key2 = b"\x00\x00\x00\x00"
    items = {}
    total = 0
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.settimeout(timeout)
        s.sendall(_ahsrch_build_category_request(cat, key2))
        guard = 0
        is_last = False
        while not is_last and guard < 80:
            page = _ahsrch_parse_listing(_ahsrch_recv_packet(s, timeout), key2)
            if page is None:
                break
            pitems, ptotal, is_last = page
            items.update(pitems)
            total = ptotal
            if is_last or len(items) >= total:
                break
            s.sendall(_ahsrch_build_more_request(key2))
            guard += 1
    return {"items": items, "total": total}


# ─────────────── player search / server population ───────────────
# Besides the AH, the search server answers a player-search family (retail
# /search). For a population readout we don't need the (truncated) record list:
# every reply carries the TRUE match count as a u16 at 0x0E ("total found, may
# differ from the amount sent"), and the query behind it has no LIMIT — so one
# broad search returns the live server population.
#
# The request framing is identical to the AH requests above; the only deltas are
# the type byte (0x03 search / 0x00 search-all) and a bit-packed filter payload:
# a byte count at 0x10, then entries from 0x11. Each entry is a 5-bit tag, then
# (for most tags) a 1-bit sort flag + 1-bit "present" flag, then the value bits.
# Verified by round-tripping a built request back through the server's own
# decrypt + hash-check + bit-unpack logic.
_AHSRCH_MASK64 = 0xFFFFFFFFFFFFFFFF

_AHSRCH_TCP_SEARCH_ALL = 0x00
_AHSRCH_TCP_SEARCH     = 0x03

# 5-bit entry tags (search filter types)
_AHSRCH_SE_NAME   = 0x00
_AHSRCH_SE_AREA   = 0x01
_AHSRCH_SE_NATION = 0x02
_AHSRCH_SE_JOB    = 0x03
_AHSRCH_SE_LEVEL  = 0x04


def _ahsrch_packbits_be(target, value, byte_off, bit_off, nbits):
    byte_off += bit_off >> 3
    bit_off %= 8
    bitmask = (_AHSRCH_MASK64 >> (64 - nbits)) << bit_off
    value = ((value << bit_off) & _AHSRCH_MASK64) & bitmask
    bitmask ^= _AHSRCH_MASK64
    ab = (bit_off + nbits + 7) // 8
    data = int.from_bytes(bytes(target[byte_off:byte_off + ab]), "little")
    data = ((data & bitmask) | value) & ((1 << (ab * 8)) - 1)
    target[byte_off:byte_off + ab] = data.to_bytes(ab, "little")


def _ahsrch_packbits_le(target, value, bit_off, nbits):
    # Port of the search protocol's little-endian bit-packer. `bit_off` is an
    # absolute bit offset into target; returns the new absolute bit offset.
    byte_off = bit_off >> 3
    bit_off %= 8
    t = bit_off + nbits
    need = 1 if t <= 8 else 2 if t <= 16 else 4 if t <= 32 else 8
    ab = (bit_off + nbits + 7) // 8
    m = bytearray(need)
    for c in range(ab):
        m[need - 1 - c] = target[byte_off + c]
    _ahsrch_packbits_be(m, value, 0, (need << 3) - (bit_off + nbits), nbits)
    for c in range(ab):
        target[byte_off + c] = m[need - 1 - c]
    return (byte_off << 3) + bit_off + nbits


def _ahsrch_build_search_request(job=None, min_lvl=None, max_lvl=None,
                                 areas=None, nation=None, search_all=True,
                                 key2=b"\x00\x00\x00\x00", key_tail=None):
    # Build a player-search request. With no filters the reply's Total is the
    # whole-server online population; pass job=<id> for a per-job count, etc.
    if key_tail is None:
        key_tail = os.urandom(4)
    pl = bytearray(48)
    off = 0

    def _entry(tag, present, descending=0):
        nonlocal off
        off = _ahsrch_packbits_le(pl, tag, off, 5)
        off = _ahsrch_packbits_le(pl, descending, off, 1)
        off = _ahsrch_packbits_le(pl, present, off, 1)

    if job is not None:
        _entry(_AHSRCH_SE_JOB, 1)
        off = _ahsrch_packbits_le(pl, job & 0x1F, off, 5)
    if min_lvl is not None or max_lvl is not None:
        _entry(_AHSRCH_SE_LEVEL, 1)
        off = _ahsrch_packbits_le(pl, (min_lvl or 0) & 0xFF, off, 8)
        off = _ahsrch_packbits_le(pl, (max_lvl or 0) & 0xFF, off, 8)
    if nation is not None:
        _entry(_AHSRCH_SE_NATION, 1)
        off = _ahsrch_packbits_le(pl, nation & 0x3, off, 2)
    if areas:
        for a in areas:
            _entry(_AHSRCH_SE_AREA, 1)
            off = _ahsrch_packbits_le(pl, a & 0x3FF, off, 10)
        _entry(_AHSRCH_SE_AREA, 0)  # area-list terminator

    nbytes = (off + 7) // 8
    length = 76
    if 0x11 + nbytes > length - 0x18:
        raise ValueError("search filter payload too large (%d bytes)" % nbytes)
    buf = bytearray(length)
    _ahsrch_struct.pack_into("<H", buf, 0x00, length)
    _ahsrch_struct.pack_into("<I", buf, 0x04, _AHSRCH_IXFF)
    _ahsrch_struct.pack_into("<H", buf, 0x08, 16)
    buf[0x0A] = 0x80
    buf[0x0B] = _AHSRCH_TCP_SEARCH_ALL if search_all else _AHSRCH_TCP_SEARCH
    buf[0x10] = nbytes
    buf[0x11:0x11 + nbytes] = pl[:nbytes]
    buf[length - 0x18:length - 0x14] = key2
    buf[length - 0x14:length - 0x04] = _ahsrch_md5(bytes(buf[0x08:length - 0x14]))
    buf[length - 0x04:length] = key_tail
    P, S = _ahsrch_blowfish_init(_ahsrch_md5(_AHSRCH_KEY_SEED + key_tail))
    _ahsrch_cipher_blocks(buf, length, P, S, decrypt=False)
    return bytes(buf)


def _ahsrch_parse_search_count(data, key2=b"\x00\x00\x00\x00"):
    # Decrypt one player-search reply and return the u16 "total found" at 0x0E
    # (the reply's type byte at 0x0B is 0x80). None on failure.
    if len(data) < 28:
        return None
    buf = bytearray(data)
    length = _ahsrch_struct.unpack_from("<H", buf, 0)[0]
    if length < 28 or length > len(buf):
        return None
    P, S = _ahsrch_blowfish_init(_ahsrch_md5(
        _AHSRCH_KEY_SEED + bytes(buf[length - 4:length]) + key2))
    _ahsrch_cipher_blocks(buf, length, P, S, decrypt=True)
    if buf[0x0B] != 0x80:
        return None
    return _ahsrch_struct.unpack_from("<H", buf, 0x0E)[0]


def _ahsrch_query_population(host, port=_AHSRCH_PORT, timeout=8.0, **filters):
    # Fire one broad player search and read Total from the first reply packet
    # (every packet carries it; no need to page the record list). No filters =
    # whole-server online population.
    req = _ahsrch_build_search_request(**filters)
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.settimeout(timeout)
        s.sendall(req)
        data = _ahsrch_recv_packet(s, timeout)
    return _ahsrch_parse_search_count(data)


def _ahsrch_median_price(host, item_id, stack=0, port=_AHSRCH_PORT,
                         timeout=6.0):
    # Median of one item's recent AH sale prices on one world (or None). This
    # is the same history query the detail pane uses, just reduced to a median
    # so it can be fanned out across all worlds for a price comparison.
    try:
        raw = _ahsrch_query_history(host, port, item_id, stack, timeout=timeout)
        res = _ahsrch_parse_history(raw)
    except Exception:
        return None
    if not res.get("ok"):
        return None
    prices = [s.get("price", 0) for s in res.get("sales", []) if s.get("price")]
    if not prices:
        return None
    return int(statistics.median(prices))


# --- panel glue: session-cached IP, threaded fetch, main-thread drain ---
_ah_search_ip = None
_ah_hist_inbox = _collections.deque()
_ah_hist_busy = False


def _ah_hist_emit(line):
    """Show an AH-history line in the panel results pane AND mirror it (full,
    untruncated) to the session log. `line` is a plain str, or a list of
    (text, color) segments for coloured rendering."""
    _ah_hist_inbox.append(line)
    try:
        flat = line if isinstance(line, str) else "".join(t for t, _c in line)
        print("[AH-history] " + flat)
    except Exception:
        pass


def _ah_item_name(item_id):
    try:
        for it in ah_state.get("items", []):
            if it.get("id") == item_id:
                return it.get("name") or ("item %d" % item_id)
    except Exception:
        pass
    return "item %d" % item_id


def _ahsrch_build_history_request(item_id, stack, key2=b"\x00\x00\x00\x00", key_tail=None):
    # Exact real-client AH-history request (verified byte-for-byte against a
    # live capture): itemid as u16 @0x12, constant 0x04 @0x14, stack flag @0x15,
    # opcode 0x05 single / 0x06 stack. No 0x0E / param framing (the listing
    # request uses those; history does not).
    if key_tail is None:
        key_tail = os.urandom(4)
    length = 268
    buf = bytearray(length)
    _ahsrch_struct.pack_into("<H", buf, 0x00, length)
    _ahsrch_struct.pack_into("<I", buf, 0x04, _AHSRCH_IXFF)
    _ahsrch_struct.pack_into("<H", buf, 0x08, 184)
    buf[0x0A] = 0x80
    buf[0x0B] = 0x06 if stack else 0x05
    _ahsrch_struct.pack_into("<H", buf, 0x12, item_id & 0xFFFF)
    buf[0x14] = 0x04
    buf[0x15] = 0x01 if stack else 0x00
    buf[length - 0x18:length - 0x14] = key2
    buf[length - 0x14:length - 0x04] = _ahsrch_md5(bytes(buf[0x08:length - 0x14]))
    buf[length - 0x04:length] = key_tail
    P, S = _ahsrch_blowfish_init(_ahsrch_md5(_AHSRCH_KEY_SEED + key_tail))
    _ahsrch_cipher_blocks(buf, length, P, S, decrypt=False)
    return bytes(buf)


def _ahsrch_query_history(host, port, item_id, stack, timeout=8.0):
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.settimeout(timeout)
        s.sendall(_ahsrch_build_history_request(item_id, stack))
        return _ahsrch_recv_packet(s, timeout)


def _ahsrch_parse_history(data, key2=b"\x00\x00\x00\x00"):
    # Decrypt + parse a history reply (0x85 single / 0x86 stack). Item header at
    # 0x18 (itemid u16, total-sold u32 @0x1A, category u16 @0x1E); up to 10 sale
    # records from 0x20, 40 bytes each: price u32, date u32 (unix), seller 16B,
    # buyer 16B.
    if len(data) < 28:
        return {"ok": False, "raw": data}
    buf = bytearray(data)
    length = _ahsrch_struct.unpack_from("<H", buf, 0)[0]
    if length < 28 or length > len(buf):
        return {"ok": False, "raw": data}
    P, S = _ahsrch_blowfish_init(_ahsrch_md5(
        _AHSRCH_KEY_SEED + bytes(buf[length - 4:length]) + key2))
    _ahsrch_cipher_blocks(buf, length, P, S, decrypt=True)
    if _ahsrch_md5(bytes(buf[8:length - 0x14])) != bytes(buf[length - 0x14:length - 0x04]):
        return {"ok": False, "raw": data, "badhash": True}
    if (buf[0x0B] & 0x1F) not in (0x05, 0x06):
        return {"ok": False, "raw": data, "type": buf[0x0B]}
    item = _ahsrch_struct.unpack_from("<H", buf, 0x18)[0]
    count = _ahsrch_struct.unpack_from("<I", buf, 0x1A)[0]
    cat = _ahsrch_struct.unpack_from("<H", buf, 0x1E)[0]
    marker = _ahsrch_struct.unpack_from("<H", buf, 0x08)[0]
    nrec = max(0, (marker - 0x20) // 40)
    sales = []
    for i in range(nrec):
        o = 0x20 + 40 * i
        if o + 40 > length - 0x14:
            break
        sales.append({
            "price": _ahsrch_struct.unpack_from("<I", buf, o + 0x00)[0],
            "date": _ahsrch_struct.unpack_from("<I", buf, o + 0x04)[0],
            "seller": _ahsrch_decode_name(bytes(buf[o + 0x08:o + 0x18])),
            "buyer": _ahsrch_decode_name(bytes(buf[o + 0x18:o + 0x28])),
        })
    return {"ok": True, "item": item, "count": count, "cat": cat,
            "marker": marker, "sales": sales}



# ─────────────────────────── item database ───────────────────────────
def _load_items():
    cands = []
    # PyInstaller --onefile: bundled data lands in sys._MEIPASS
    mei = getattr(sys, "_MEIPASS", None)
    if mei:
        cands.append(os.path.join(mei, "ffxi_items.json"))
    here = os.path.dirname(os.path.abspath(
        sys.argv[0] if getattr(sys, "frozen", False) else __file__))
    cands.append(os.path.join(here, "ffxi_items.json"))
    cands.append("ffxi_items.json")
    for c in cands:
        if os.path.isfile(c):
            with open(c, encoding="utf-8") as f:
                return json.load(f)
    return {}


ITEMS = _load_items()   # {"id": {"n": name, "c": cat, "s": stack, "d": desc}}
_NAME_INDEX = sorted(((v.get("n", ""), int(k)) for k, v in ITEMS.items()),
                     key=lambda t: t[0].lower())


def search_items(q, limit=300):
    q = q.strip().lower()
    if not q:
        return []
    hits = [(n, i) for (n, i) in _NAME_INDEX if q in n.lower()]
    # prefix matches first, then alphabetical within each group
    hits.sort(key=lambda t: (0 if t[0].lower().startswith(q) else 1,
                             t[0].lower()))
    return hits[:limit]


_JOB_ABBR = {1: "WAR", 2: "MNK", 3: "WHM", 4: "BLM", 5: "RDM", 6: "THF",
             7: "PLD", 8: "DRK", 9: "BST", 10: "BRD", 11: "RNG", 12: "SAM",
             13: "NIN", 14: "DRG", 15: "SMN", 16: "BLU", 17: "COR", 18: "PUP",
             19: "DNC", 20: "SCH", 21: "GEO", 22: "RUN"}
_NJOBS = 22
_SLOT_NAME = {0: "Main", 1: "Sub", 2: "Range", 3: "Ammo", 4: "Head", 5: "Body",
              6: "Hands", 7: "Legs", 8: "Feet", 9: "Neck", 10: "Waist",
              11: "L.Ear", 12: "R.Ear", 13: "L.Ring", 14: "R.Ring", 15: "Back"}


def _jobs_str(mask):
    if not mask:
        return ""
    on = [_JOB_ABBR[j] for j in range(1, _NJOBS + 1) if mask & (1 << j)]
    if len(on) == _NJOBS:
        return "All jobs"
    return " ".join(on)


def _slot_str(mask):
    if not mask:
        return ""
    txt = "/".join(_SLOT_NAME[s] for s in range(16) if mask & (1 << s))
    return txt.replace("L.Ear/R.Ear", "Ears").replace("L.Ring/R.Ring", "Rings")


def _fmt_ts(ts):
    # local date + time of the sale (the timestamp is a unix epoch)
    try:
        dt = datetime.datetime.fromtimestamp(ts)
        return dt.strftime("%Y-%m-%d") + "     " + dt.strftime("%H:%M")
    except Exception:
        return str(ts)


# ─────────────────────────── servers ───────────────────────────
# The 16 live FFXI worlds. Each has its own search server; the address is
# user-supplied per world and remembered in %APPDATA%/FFXI_AH_Browser.
_WORLDS = ["Asura", "Bahamut", "Bismarck", "Carbuncle", "Cerberus", "Fenrir",
           "Lakshmi", "Leviathan", "Odin", "Phoenix", "Quetzalcoatl",
           "Ragnarok", "Shiva", "Siren", "Sylph", "Valefor"]
_DEFAULT_SERVERS = {
    "Asura": "124.150.154.76",
    "Bahamut": "124.150.154.61",
    "Bismarck": "124.150.154.74",
    "Carbuncle": "124.150.154.64",
    "Cerberus": "124.150.154.73",
    "Fenrir": "124.150.154.65",
    "Lakshmi": "124.150.154.75",
    "Leviathan": "124.150.154.68",
    "Phoenix": "124.150.154.63",
    "Quetzalcoatl": "124.150.154.70",
    "Ragnarok": "124.150.154.72",
    "Shiva": "124.150.154.62",
    "Siren": "124.150.154.71",
    "Sylph": "124.150.154.66",
    "Odin": "124.150.154.69",
    "Valefor": "124.150.154.67",
    # All 16 live worlds occupy 124.150.154.61-.76. If SE ever renumbers one,
    # Detect on that world re-reads it and Save overrides the default locally.
}


def _servers_path():
    base = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"),
                        "AuctionWatch")
    return os.path.join(base, "servers.json")


def _load_servers():
    d = dict(_DEFAULT_SERVERS)
    try:
        with open(_servers_path(), encoding="utf-8") as f:
            saved = json.load(f)
        if isinstance(saved, dict):
            d.update({k: v for k, v in saved.items() if isinstance(v, str)})
    except Exception:
        pass
    return d


def _ui_path():
    base = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"),
                        "AuctionWatch")
    return os.path.join(base, "ui.json")


def _load_ui():
    try:
        with open(_ui_path(), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _save_ui(d):
    try:
        p = _ui_path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass


def _save_servers(d):
    try:
        p = _servers_path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ─────────────────────────── the app ───────────────────────────
class AHBrowser(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AuctionWatch")
        self._ui = _load_ui()
        self.configure(bg="#1e1e28")
        self._ui_save_after = None
        self._build()
        self.update_idletasks()
        self.geometry(self._ui.get("geometry", "980x620"))
        self.after(120, self._restore_sash)
        self.bind("<Configure>", self._on_configure)
        self.tree.bind("<ButtonRelease-1>",
                       lambda e: self._schedule_ui_save(), add="+")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._cur_id = None
        self._pop_busy = False
        self._cat_cache = {}   # AH category -> {itemid: (singles, stacks)}
        self._xs_cache = {}    # item_id -> [(world, median), ...] this session
        self._hist_rows = []
        self._sort_col = "date"
        self._sort_rev = True   # newest first by default
        self.after(400, self._refresh_population)

    def _build(self):
        top = tk.Frame(self, bg="#1e1e28")
        top.pack(fill="x", padx=8, pady=6)
        tk.Label(top, text="Search:", bg="#1e1e28", fg="#dcdce6").pack(side="left")
        self.q = tk.Entry(top, width=30)
        self.q.pack(side="left", padx=6)
        self.q.bind("<KeyRelease>", lambda e: self._do_search())
        self.q.focus_set()
        self._servers = _load_servers()
        tk.Label(top, text="World:", bg="#1e1e28", fg="#dcdce6").pack(
            side="left", padx=(16, 0))
        self.world = ttk.Combobox(top, values=_WORLDS, width=12,
                                  state="readonly")
        self.world.set(self._ui.get("world", "Phoenix"))
        self.world.pack(side="left", padx=6)
        self.world.bind("<<ComboboxSelected>>", lambda e: self._world_changed())
        tk.Label(top, text="Address:", bg="#1e1e28", fg="#dcdce6").pack(
            side="left")
        self.server = tk.Entry(top, width=16)
        self.server.insert(0, self._servers.get(self.world.get(), ""))
        self.server.pack(side="left", padx=6)
        tk.Button(top, text="Save", command=self._save_addr).pack(
            side="left", padx=2)
        tk.Button(top, text="Detect", command=self._detect).pack(
            side="left", padx=2)
        tk.Button(top, text="Default",
                  command=self._set_default_world).pack(side="left", padx=2)
        self.status = tk.Label(top, text="",
                               bg="#1e1e28", fg="#8a90a2")
        self.status.pack(side="right")

        # bottom: thin live server-population strip.
        self.popsec = tk.Frame(self, bg="#181820")
        self.popsec.pack(side="bottom", fill="x", padx=8, pady=(0, 6))
        self.pop_total_lbl = tk.Label(self.popsec, text="population \u2014",
                                      bg="#181820", fg="#8fd39a",
                                      font=("Segoe UI", 10))
        self.pop_total_lbl.pack(side="left", padx=(4, 0), pady=2)
        tk.Button(self.popsec, text="Refresh",
                  command=self._refresh_population).pack(side="right", padx=4,
                                                         pady=2)

        body = self.body = tk.PanedWindow(self, sashwidth=4, bg="#2a2a38")
        body.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        body.bind("<ButtonRelease-1>",
                  lambda e: self._schedule_ui_save(), add="+")

        # left: results
        left = tk.Frame(body, bg="#1e1e28")
        self.results = tk.Listbox(left, activestyle="none", bg="#14141c",
                                  fg="#c8cede", highlightthickness=0,
                                  selectbackground="#33415c", width=34)
        # cross-server median-price ranking for the selected item, filling the
        # empty results-panel space (all 16 worlds queried in parallel).
        self.xserver = tk.Listbox(left, activestyle="none", bg="#12121a",
                                  fg="#c8cede", highlightthickness=0, height=16,
                                  selectbackground="#33415c",
                                  font=("Consolas", 9))
        self.xserver.pack(side="bottom", fill="x")
        self.xs_lbl = tk.Label(left, text="", bg="#1e1e28", fg="#8a90a2",
                               anchor="w", font=("Segoe UI", 8))
        self.xs_lbl.pack(side="bottom", fill="x", padx=2, pady=(4, 1))
        self.results.pack(fill="both", expand=True)
        self.results.bind("<<ListboxSelect>>", lambda e: self._pick())
        self.results.bind("<Button-3>", self._results_rightclick)
        body.add(left, minsize=220)

        # right: detail
        right = tk.Frame(body, bg="#1e1e28")
        self.name_lbl = tk.Label(right, text="", bg="#1e1e28", fg="#e6d29a",
                                 font=("Segoe UI", 14, "bold"), anchor="w")
        self.name_lbl.pack(fill="x", padx=8, pady=(6, 0))
        self.meta_lbl = tk.Label(right, text="", bg="#1e1e28", fg="#9aa0b2",
                                 anchor="w")
        self.meta_lbl.pack(fill="x", padx=8)
        self.jobs_lbl = tk.Label(right, text="", bg="#1e1e28", fg="#9ab0d0",
                                 anchor="w", justify="left", wraplength=560)
        self.jobs_lbl.pack(fill="x", padx=8)
        self.desc_lbl = tk.Label(right, text="", bg="#1e1e28", fg="#c2c8d6",
                                 anchor="w", justify="left", wraplength=560)
        self.desc_lbl.pack(fill="x", padx=8, pady=(4, 8))

        cols = ("date", "price", "seller", "buyer")
        hdr = tk.Frame(right, bg="#1e1e28"); hdr.pack(fill="x", padx=8)
        self.hist_lbl = tk.Label(hdr, text="Auction history", bg="#1e1e28",
                                 fg="#dcdce6", font=("Segoe UI", 10, "bold"))
        self.hist_lbl.pack(side="left")
        self._type_filter = "all"
        self._onsale = None
        self._filter_btns = {}
        fbf = tk.Frame(hdr, bg="#1e1e28")
        fbf.pack(side="left", padx=12)
        for key, lbl in (("all", "All"), ("single", "Singles"),
                         ("stack", "Stacks")):
            b = tk.Button(fbf, text=lbl, relief="flat", bd=0, bg="#2a2a38",
                          fg="#c8cede", activebackground="#33415c",
                          padx=8, pady=0,
                          command=lambda k=key: self._set_filter(k))
            b.pack(side="left", padx=1)
            self._filter_btns[key] = b
        self._filter_btns["all"].config(bg="#33415c")
        self.summary = tk.Label(hdr, text="", bg="#1e1e28", fg="#8fd39a")
        self.summary.pack(side="right")

        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=16)
        self._col_titles = {"date": "Sold (date / time)", "price": "Price",
                            "seller": "Seller", "buyer": "Buyer"}
        for c, w in (("date", 150), ("price", 100), ("seller", 115),
                     ("buyer", 115)):
            self.tree.heading(c, text=self._col_titles[c],
                              command=lambda cc=c: self._sort_by(cc))
            self.tree.column(c, width=self._ui.get("cols", {}).get(c, w),
                             anchor="w", stretch=False)
        self.tree.pack(fill="both", expand=True, padx=8, pady=(2, 8))
        body.add(right, minsize=520)

    def _world_changed(self):
        w = self.world.get()
        addr = self._servers.get(w, "")
        self.server.delete(0, "end")
        self.server.insert(0, addr)
        self._cat_cache = {}          # listings are per-server; drop stale cache
        # server/address already show in the toolbar; don't repeat them here.
        if addr:
            self.status.config(text="")
            self._refresh_population()
        else:
            self.status.config(text="%s: no address yet -- type it and Save" % w)
        # if an item is up and this world has an address, re-pull it live
        if self._cur_id is not None and addr:
            self._refresh_current()

    def _detect(self):
        # Find the current world's search server from this PC's live TCP
        # table (the game must be running / recently /search'd on that world).
        self.status.config(text="detecting current world's server\u2026")

        def _worker():
            try:
                ip = _ahsrch_find_server()
            except Exception:
                ip = None

            def _apply():
                if ip:
                    self.server.delete(0, "end")
                    self.server.insert(0, ip)
                    self.status.config(
                        text="detected %s  \u2014  pick the world, then Save" % ip)
                else:
                    self.status.config(
                        text="not found \u2014 /search in-game on this world first")
            self.after(0, _apply)
        threading.Thread(target=_worker, daemon=True).start()

    def _current_host(self):
        # Prefer the address box; fall back to the world map / auto-detect.
        ip = self.server.get().strip()
        return ip or _ahsrch_resolve_host(self.world.get())

    def _refresh_population(self):
        if getattr(self, "_pop_busy", False):
            return
        world = self.world.get()
        host = self._current_host()
        if not host:
            self.pop_total_lbl.config(text="%s \u2014 no address" % world,
                                      fg="#d39a9a")
            return
        self._pop_busy = True
        self.pop_total_lbl.config(text="%s \u2014 querying\u2026" % world,
                                  fg="#8a90a2")

        def _worker():
            try:
                total = _ahsrch_query_population(host)
            except Exception:
                total = None

            def _apply():
                self._pop_busy = False
                if total is None:
                    self.pop_total_lbl.config(text="%s \u2014 no reply" % world,
                                              fg="#d39a9a")
                else:
                    self.pop_total_lbl.config(
                        text="%s \u2014 %s online" % (world, format(total, ",")),
                        fg="#8fd39a")
            self.after(0, _apply)
        threading.Thread(target=_worker, daemon=True).start()


    def _set_default_world(self):
        # remember the current world so it opens automatically next launch.
        w = self.world.get()
        self._ui["world"] = w
        self._save_ui_state()
        self.status.config(text="%s will open by default" % w)

    def _save_addr(self):
        w = self.world.get()
        ip = self.server.get().strip()
        self._servers[w] = ip
        _save_servers(self._servers)
        self.status.config(text="saved  %s -> %s" % (w, ip or "(blank)"))

    def _on_configure(self, event):
        if event.widget is self:
            self._schedule_ui_save()

    def _schedule_ui_save(self):
        # debounce: save 700ms after the last resize / column drag
        if self._ui_save_after is not None:
            try:
                self.after_cancel(self._ui_save_after)
            except Exception:
                pass
        self._ui_save_after = self.after(700, self._save_ui_state)

    def _save_ui_state(self):
        self._ui_save_after = None
        try:
            cols = {c: int(self.tree.column(c, "width"))
                    for c in ("date", "price", "seller", "buyer")}
            state = {"geometry": self.geometry(), "cols": cols}
            if self._ui.get("world"):
                state["world"] = self._ui["world"]
            try:
                state["sash"] = int(self.body.sash_coord(0)[0])
            except Exception:
                pass
            _save_ui(state)
        except Exception:
            pass

    def _restore_sash(self):
        # left-panel width persists across runs; default a bit wide so the
        # cross-server header is fully readable on first launch.
        try:
            self.body.sash_place(0, int(self._ui.get("sash", 300)), 1)
        except Exception:
            pass

    def _on_close(self):
        self._save_ui_state()
        self.destroy()

    def _results_rightclick(self, event):
        idx = self.results.nearest(event.y)
        if idx is None or idx < 0 or idx >= len(getattr(self, "_hits", [])):
            return
        self.results.selection_clear(0, "end")
        self.results.selection_set(idx)
        name, iid = self._hits[idx]
        ffxiah = "https://www.ffxiah.com/item/%d" % iid
        bgwiki = "https://www.bg-wiki.com/ffxi/" + name.replace(" ", "_")
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Open on FFXIAH",
                         command=lambda: webbrowser.open(ffxiah))
        menu.add_command(label="Open on BG-wiki",
                         command=lambda: webbrowser.open(bgwiki))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _do_search(self):
        self.results.delete(0, "end")
        self._hits = search_items(self.q.get())
        for (n, i) in self._hits:
            self.results.insert("end", n)

    def _pick(self):
        sel = self.results.curselection()
        if not sel:
            return
        name, iid = self._hits[sel[0]]
        self._cur_id = iid
        it = ITEMS.get(str(iid), {})
        self.name_lbl.config(text=name)
        bits = ["id %d" % iid]
        if it.get("re"):
            bits.append(it["re"])
        sl = _slot_str(it.get("sl", 0))
        if sl:
            bits.append(sl)
        if it.get("lv"):
            bits.append("Lv %d" % it["lv"])
        if it.get("il"):
            bits.append("iLv %d" % it["il"])
        bits.append(it.get("c", "?"))
        if it.get("s", 1) > 1:
            bits.append("stack %d" % it["s"])
        self.meta_lbl.config(text="   \u00b7   ".join(bits))
        js = _jobs_str(it.get("j", 0))
        self.jobs_lbl.config(text=("Jobs:  " + js) if js else "")
        self.desc_lbl.config(text=it.get("d", ""))
        self._refresh_current()
        self._refresh_population()
        self._compare_servers(iid)

    def _refresh_current(self):
        iid = self._cur_id
        if iid is None:
            return
        for r in self.tree.get_children():
            self.tree.delete(r)
        self.summary.config(text="")
        self.hist_lbl.config(text="Auction history  —  loading…")
        threading.Thread(target=self._load_history, args=(iid,),
                         daemon=True).start()

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            # sensible first click: newest / highest / A-Z
            self._sort_rev = col in ("date", "price")
        self._render_rows()

    def _set_filter(self, k):
        self._type_filter = k
        for key, b in self._filter_btns.items():
            b.config(bg="#33415c" if key == k else "#2a2a38")
        self._render_rows()

    def _render_rows(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = self._hist_rows
        if self._type_filter != "all":
            rows = [r for r in rows if r[3] == self._type_filter]
        keyfns = {
            "date": lambda r: r[0],
            "price": lambda r: r[2],
            "seller": lambda r: (r[4] or "").lower(),
            "buyer": lambda r: (r[5] or "").lower(),
        }
        kf = keyfns.get(self._sort_col, keyfns["date"])
        rows = sorted(rows, key=kf, reverse=self._sort_rev)
        for (_ts, dstr, price, tag, seller, buyer) in rows:
            ptxt = f"{price:,}" + ("  (stack)" if tag == "stack" else "")
            self.tree.insert("", "end", values=(dstr, ptxt, seller, buyer))
        for c, base in self._col_titles.items():
            arrow = ""
            if c == self._sort_col:
                arrow = "  \u25bc" if self._sort_rev else "  \u25b2"
            self.tree.heading(c, text=base + arrow)
        # summary follows the current filter
        def _n(v):
            return "n/a" if v == 0xFFFFFFFF else str(v)
        parts = []
        if self._onsale is not None:
            parts.append("on sale now: %s single / %s stack"
                         % (_n(self._onsale[0]), _n(self._onsale[1])))
        fprices = [r[2] for r in rows]
        if fprices:
            lo, hi = min(fprices), max(fprices)
            med = int(statistics.median(fprices))
            lbl = {"single": "single ", "stack": "stack "}.get(
                self._type_filter, "")
            parts.append(f"{lbl}low {lo:,}  ·  med {med:,}  ·  high {hi:,} g")
        self.summary.config(text="      |      ".join(parts))
        if self._hist_rows or self._onsale is not None:
            self.hist_lbl.config(text="Auction history")
        else:
            self.hist_lbl.config(text="Auction history  —  no data / no answer")

    def _compare_servers(self, iid):
        # Fan the item's median-price query out across every world with a known
        # address, in parallel, and rank cheapest -> priciest in the left panel.
        cached = self._xs_cache.get(iid)
        if cached is not None:
            self._render_xservers(iid, cached)
            return
        worlds = [(w, self._servers.get(w)) for w in _WORLDS
                  if self._servers.get(w)]
        if not worlds:
            return
        self.xserver.delete(0, "end")
        self.xs_lbl.config(text="comparing %d servers\u2026" % len(worlds))

        def _worker():
            import concurrent.futures as _cf
            results = []
            try:
                with _cf.ThreadPoolExecutor(max_workers=len(worlds)) as ex:
                    fut = {ex.submit(_ahsrch_median_price, ip, iid): w
                           for w, ip in worlds}
                    for f in _cf.as_completed(fut):
                        try:
                            med = f.result()
                        except Exception:
                            med = None
                        if med is not None:
                            results.append((fut[f], med))
            except Exception:
                pass
            results.sort(key=lambda t: t[1])
            self._xs_cache[iid] = results
            self.after(0, lambda: self._render_xservers(iid, results))
        threading.Thread(target=_worker, daemon=True).start()

    def _render_xservers(self, iid, results):
        if iid != self._cur_id:
            return   # user moved to another item; drop stale result
        self.xserver.delete(0, "end")
        if not results:
            self.xs_lbl.config(text="no single-sale history on any server")
            return
        self.xs_lbl.config(text="median price by server (singles, cheapest first)")
        for world, med in results:
            self.xserver.insert("end", " %-13s %13s g" % (world, format(med, ",")))
        self.xserver.itemconfig(0, fg="#8fd39a")                 # cheapest
        self.xserver.itemconfig(len(results) - 1, fg="#e39a9a")  # priciest

    def _load_history(self, iid):
        host = self.server.get().strip()
        w = self.world.get()
        if host and self._servers.get(w) != host:
            self._servers[w] = host
            _save_servers(self._servers)   # remember whatever they typed
        if not host:
            self.after(0, lambda: self.hist_lbl.config(
                text="Auction history  —  set an Address for %s (then Save)" % w))
            return
        rows, prices, cat = [], [], None
        for stack in (0, 1):
            try:
                raw = _ahsrch_query_history(host, _AHSRCH_PORT, iid, stack,
                                            timeout=8.0)
                res = _ahsrch_parse_history(raw)
            except Exception as e:
                res = {"ok": False, "err": repr(e)}
            if res.get("ok"):
                if cat is None:
                    cat = res.get("cat")
                for sv in res.get("sales", []):
                    tag = "stack" if stack else "single"
                    rows.append((sv.get("date", 0),
                                 _fmt_ts(sv.get("date", 0)),
                                 sv.get("price", 0), tag,
                                 sv.get("seller", ""), sv.get("buyer", "")))
                    prices.append(sv.get("price", 0))
        # how many are CURRENTLY on sale (live listings from the category page)
        onsale = None
        if cat:
            try:
                avail = self._cat_cache.get(cat)
                if avail is None:
                    avail = _ahsrch_query_category(host, _AHSRCH_PORT, cat,
                                                   timeout=8.0)["items"]
                    self._cat_cache[cat] = avail
                onsale = avail.get(iid, (0xFFFFFFFF, 0xFFFFFFFF))
            except Exception:
                onsale = None
        if iid != self._cur_id:
            return   # user moved on
        self.after(0, lambda: self._show_history(rows, prices, onsale))

    def _show_history(self, rows, prices, onsale):
        self._hist_rows = rows
        self._onsale = onsale
        self._render_rows()


def _ahsrch_resolve_host(arg=None):
    # Resolve a server argument: an explicit IPv4, a world name (from the saved
    # server map), else auto-detect from this PC's TCP table, else the default.
    if arg:
        if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", arg):
            return arg
        for name, ip in _load_servers().items():
            if name.lower() == arg.lower():
                return ip
    return _ahsrch_find_server() or _DEFAULT_SERVER


def main():
    if not ITEMS:
        root = tk.Tk(); root.withdraw()
        from tkinter import messagebox
        messagebox.showerror("AuctionWatch",
                             "ffxi_items.json not found next to the app.")
        return
    AHBrowser().mainloop()


if __name__ == "__main__":
    main()