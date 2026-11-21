#!/usr/bin/env python3
"""news-image-20261121: draw one image summing up the world news of
Saturday 21 November 2026 and write it to $MAKEFUN_OUTPUT_DIR/entry.png.

Python 3.13, standard library only, no network. The picture is drawn
from scratch with a small rasteriser (rects, circles, polygons, lines
and a hand-built 5x7 bitmap font), so two runs write byte-identical
PNG files. Nothing is copied in from anywhere: every shape and letter
is produced by the code in this file.

Layout (1024 x 1024), a newspaper front page:
  masthead  "21 NOVEMBER 2026" (Saturday)
  lead      Russian missiles land in Poland; NATO chief in Warsaw today
  grid      Wall Street correction / UK-EU deals / missiles over Riyadh
            / India v New Zealand cricket
  ticker    pancreatic-cancer pill, asteroid 2026 WA1, youth protests
"""

import os
import struct
import zlib
from math import sqrt

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# Hand-built 5x7 bitmap font, uppercase + digits + punctuation.
# Each glyph is 7 rows of 5 bits ("#" = ink).
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '"': ["01010", "01010", "01010", "00000", "00000", "00000", "00000"],
}


def text_width(text, scale, spacing=None):
    """Width in pixels of `text` drawn at `scale` (px per font cell unit)."""
    if spacing is None:
        spacing = max(1, scale // 2)
    return len(text) * (5 * scale + spacing) - spacing


def wrap_text(text, scale, max_width, spacing=None):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    if spacing is None:
        spacing = max(1, scale // 2)
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, spacing) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def _clip(self, x0, y0, x1, y1):
        x0 = max(0, min(self.w, x0))
        y0 = max(0, min(self.h, y0))
        x1 = max(0, min(self.w, x1))
        y1 = max(0, min(self.h, y1))
        return x0, y0, x1, y1

    def fill_rect(self, x, y, w, h, color):
        x0, y0, x1, y1 = self._clip(x, y, x + w, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:base + len(row)] = row

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x0, x1, y, color, t=1):
        self.fill_rect(x0, y - t // 2, x1 - x0, t, color)

    def vline(self, x, y0, y1, color, t=1):
        self.fill_rect(x - t // 2, y0, t, y1 - y0, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(sqrt(r * r - dy * dy))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, t=2):
        for dy in range(-r, r + 1):
            dx = int(sqrt(r * r - dy * dy))
            dx2 = int(sqrt(max(0, (r - t) * (r - t) - dy * dy))) if abs(dy) < r - t else 0
            self.fill_rect(cx - dx, cy + dy, dx - dx2 + 1, 1, color)
            self.fill_rect(cx + dx2, cy + dy, dx - dx2 + 1, 1, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        r = max(1, t // 2)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            self.circle(x, y, r, color)

    def polygon(self, points, color):
        """Scanline fill of a simple polygon (list of (x, y))."""
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, color)

    def text(self, x, y, s, scale, color, align="left"):
        """Draw uppercase text; y is the top. Returns the width drawn."""
        s = s.upper()
        spacing = max(1, scale // 2)
        w = text_width(s, scale, spacing)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 5 * scale + spacing
        return w

    def text_block(self, x, y, s, scale, color, max_width, line_gap=6,
                   align="left"):
        """Wrapped text block; returns the y just below the last line."""
        lines = wrap_text(s, scale, max_width)
        lh = 7 * scale + line_gap
        for i, line in enumerate(lines):
            self.text(x, y + i * lh, line, scale, color, align)
        return y + len(lines) * lh


# ---------------------------------------------------------------- png
def _chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(
        ">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def png_bytes(canvas):
    raw = bytearray()
    w, h = canvas.w, canvas.h
    for y in range(h):
        raw.append(0)
        raw += canvas.px[y * w * 3:(y + 1) * w * 3]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------- palette
PAPER = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
NAVY2 = (27, 42, 74)
RED = (193, 39, 45)
ORANGE = (232, 98, 44)
GOLD = (233, 196, 106)
WHITE = (255, 255, 255)
GREY = (110, 108, 100)
GREEN = (46, 125, 50)
SKY = (135, 180, 210)


# ---------------------------------------------------------------- scenes
def star4(c, cx, cy, r, color):
    """Four-point NATO-style compass star."""
    c.polygon([(cx, cy - r), (cx + r // 4, cy - r // 4),
               (cx + r, cy), (cx + r // 4, cy + r // 4),
               (cx, cy + r), (cx - r // 4, cy + r // 4),
               (cx - r, cy), (cx - r // 4, cy - r // 4)], color)


def draw_lead_art(c, x, y, w, h):
    """Night sky over Poland: missile trails, a Polish flag, NATO star."""
    c.fill_rect(x, y, w, h, NAVY2)
    # stars
    stars = [(18, 22), (70, 60), (130, 18), (180, 70), (230, 30),
             (300, 55), (350, 20), (90, 110), (210, 120), (330, 105),
             (45, 150), (275, 150), (160, 95), (20, 190), (370, 180)]
    for sx, sy in stars:
        c.fill_rect(x + sx, y + sy, 3, 3, WHITE)
    # moon
    c.circle(x + 258, y + 42, 22, (240, 238, 220))
    c.circle(x + 250, y + 37, 18, NAVY2)
    # missile trails: three diagonal streaks, hot heads
    trails = [(40, 210, 190, 60), (120, 240, 260, 90), (200, 225, 330, 110)]
    for x0, y0, x1, y1 in trails:
        c.line(x + x0, y + y0, x + x1, y + y1, ORANGE, 7)
        c.line(x + x0, y + y0, x + x1, y + y1, GOLD, 3)
        c.circle(x + x1, y + y1, 9, GOLD)
        c.circle(x + x1, y + y1, 4, WHITE)
    # ground silhouette
    c.fill_rect(x, y + h - 78, w, 78, (13, 22, 44))
    c.polygon([(x, y + h - 78), (x + 60, y + h - 108), (x + 120, y + h - 78)],
              (13, 22, 44))
    c.polygon([(x + 260, y + h - 78), (x + 320, y + h - 118),
               (x + 380, y + h - 78)], (13, 22, 44))
    # Polish flag on a pole, bottom left
    c.fill_rect(x + 34, y + h - 74, 4, 74, (200, 200, 200))
    c.fill_rect(x + 38, y + h - 72, 74, 15, WHITE)
    c.fill_rect(x + 38, y + h - 57, 74, 15, RED)
    # NATO compass star in a ring, top right
    c.ring(x + w - 52, y + 52, 30, (120, 160, 210), 3)
    star4(c, x + w - 52, y + 52, 22, (150, 185, 225))


def draw_chart_art(c, x, y, w, h):
    """Falling market chart on a pale panel."""
    c.fill_rect(x, y, w, h, (232, 226, 208))
    c.fill_rect(x + 22, y + 18, w - 44, h - 36, WHITE)
    c.rect(x + 22, y + 18, w - 44, h - 36, INK, 2)
    # grid lines
    for gy in (y + 48, y + 78, y + 108):
        c.hline(x + 24, x + w - 26, gy, (220, 220, 220), 1)
    # falling line with a red arrowhead
    pts = [(x + 32, y + 42), (x + 56, y + 52), (x + 80, y + 48),
           (x + 104, y + 78), (x + 126, y + 112)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        c.line(x0, y0, x1, y1, RED, 5)
    c.polygon([(x + 126, y + 112), (x + 112, y + 108), (x + 124, y + 126)],
              RED)
    for px, py in pts:
        c.circle(px, py, 4, INK)
    c.text(x + 30, y + h - 48, "-3.7%", 2, RED)


def draw_flags_art(c, x, y, w, h):
    """Union Jack and EU flag side by side on a pale panel."""
    c.fill_rect(x, y, w, h, (232, 226, 208))
    # Union Jack (simplified): blue field, white diagonals, red cross
    fx, fy, fw, fh = x + 14, y + 52, 56, 36
    c.fill_rect(fx, fy, fw, fh, (0, 36, 125))
    c.polygon([(fx, fy), (fx + 12, fy), (fx + fw - 12, fy + fh),
               (fx + fw, fy + fh), (fx + fw, fy + fh - 12),
               (fx + 12, fy + fh), (fx, fy + fh), (fx, fy + 12)],
              WHITE)
    c.polygon([(fx + fw, fy), (fx + fw - 12, fy), (fx + 12, fy + fh),
               (fx, fy + fh), (fx, fy + fh - 12), (fx + fw - 12, fy + fh)],
              WHITE)
    c.fill_rect(fx, fy + fh // 2 - 4, fw, 8, RED)
    c.fill_rect(fx + fw // 2 - 4, fy, 8, fh, RED)
    # EU flag: blue field, ring of gold stars
    ex, ey, ew, eh = x + 80, y + 52, 56, 36
    c.fill_rect(ex, ey, ew, eh, (0, 51, 153))
    import math as _m
    for k in range(12):
        a = 2 * _m.pi * k / 12 - _m.pi / 2
        sx = ex + ew // 2 + int(20 * _m.cos(a))
        sy = ey + eh // 2 + int(12 * _m.sin(a))
        c.circle(sx, sy, 2, GOLD)
    # handshake: two clasped hands, abstract — two overlapping bars
    c.fill_rect(x + 18, y + 108, 114, 8, INK)
    c.polygon([(x + 30, y + 108), (x + 54, y + 96), (x + 78, y + 108)],
              GOLD)
    c.polygon([(x + 78, y + 108), (x + 102, y + 96), (x + 126, y + 108)],
              GOLD)


def draw_riyadh_art(c, x, y, w, h):
    """Night skyline with an intercepted missile burst."""
    c.fill_rect(x, y, w, h, NAVY2)
    for sx, sy in [(14, 20), (60, 44), (110, 16), (140, 60)]:
        c.fill_rect(x + sx, y + sy, 3, 3, WHITE)
    # skyline silhouettes
    c.fill_rect(x + 8, y + 78, 22, h - 78, (13, 22, 44))
    c.fill_rect(x + 38, y + 62, 26, h - 62, (13, 22, 44))
    # Kingdom Centre tower: tall slab with an inverted arch opening
    c.fill_rect(x + 72, y + 34, 30, h - 34, (13, 22, 44))
    c.polygon([(x + 72, y + 34), (x + 102, y + 34), (x + 102, y + 52),
               (x + 87, y + 70), (x + 72, y + 52)], (13, 22, 44))
    c.fill_rect(x + 84, y + 52, 6, 18, NAVY2)
    c.fill_rect(x + 112, y + 88, 20, h - 88, (13, 22, 44))
    # lit windows
    for wx in (14, 44, 78, 118):
        for wy in (92, 108, 124):
            c.fill_rect(x + wx, y + wy, 4, 5, GOLD)
    # intercept burst: starburst + falling trail
    bx, by = x + 105, y + 26
    for ang in range(0, 360, 30):
        import math as _m
        r = 16 if ang % 60 == 0 else 9
        ex = bx + int(r * _m.cos(_m.radians(ang)))
        ey = by + int(r * _m.sin(_m.radians(ang)))
        c.line(bx, by, ex, ey, GOLD, 3)
    c.circle(bx, by, 6, WHITE)
    c.line(bx - 8, by + 12, bx - 30, by + 44, ORANGE, 4)


def draw_cricket_art(c, x, y, w, h):
    """Green pitch, stumps, bat and ball."""
    c.fill_rect(x, y, w, h, (46, 125, 50))
    c.fill_rect(x, y + 96, w, h - 96, (56, 142, 60))
    # pitch strip
    c.fill_rect(x + 52, y + 20, 46, h - 20, (210, 190, 140))
    # stumps
    for sx in (66, 72, 78):
        c.fill_rect(x + sx, y + 30, 3, 26, (255, 235, 150))
    c.fill_rect(x + 65, y + 28, 17, 3, (255, 235, 150))
    # bat, leaning
    c.polygon([(x + 92, y + 96), (x + 100, y + 96), (x + 116, y + 52),
               (x + 108, y + 48)], (150, 105, 60))
    c.fill_rect(x + 108, y + 40, 5, 14, (120, 82, 45))
    # red ball mid-air with seam
    c.circle(x + 122, y + 30, 8, (178, 34, 34))
    c.line(x + 116, y + 26, x + 128, y + 34, WHITE, 1)
    # fielders' dots
    for fx, fy in [(18, 120), (130, 130), (30, 60)]:
        c.circle(x + fx, y + fy, 4, WHITE)


# ---------------------------------------------------------------- layout
def draw_masthead(c):
    c.fill_rect(0, 0, W, 108, NAVY)
    c.text(W // 2, 12, "THE WORLD IN ONE IMAGE", 2, GOLD, align="center")
    c.text(W // 2, 34, "21 NOVEMBER 2026", 6, WHITE, align="center")
    c.text(W // 2, 84, "SATURDAY", 2, (200, 205, 220), align="center")
    c.fill_rect(0, 108, W, 5, RED)


def draw_lead(c):
    y0, y1 = 120, 452
    c.fill_rect(0, y0, W, y1 - y0, WHITE)
    c.rect(0, y0, W, y1 - y0, INK, 2)
    draw_lead_art(c, 2, y0 + 2, 396, y1 - y0 - 4)
    tx = 420
    c.text(tx, y0 + 16, "LEAD STORY - POLAND / NATO", 2, RED)
    c.text(tx, y0 + 44, "MISSILES LAND", 5, INK)
    c.text(tx, y0 + 84, "IN POLAND", 5, INK)
    c.hline(tx, tx + 120, y0 + 134, RED, 4)
    c.text_block(tx, y0 + 150,
                 "NATO CHIEF IN WARSAW TODAY AS POLAND SEEKS MORE "
                 "ALLIED FORCES. TUSK: A DELIBERATE PROVOCATION. "
                 "EIGHT KILLED IN THE UKRAINE BARRAGE.",
                 3, INK, 588, line_gap=7)
    c.text(tx, y1 - 34, "NO ONE HURT IN POLAND - JETS SCRAMBLED", 2, GREY)


def draw_panel(c, x, y, w, h, art, kicker, headline, deck):
    c.fill_rect(x, y, w, h, WHITE)
    c.rect(x, y, w, h, INK, 2)
    art(c, x + 2, y + 2, 148, h - 4)
    tx = x + 166
    tw = x + w - 16 - tx
    c.text(tx, y + 14, kicker, 2, RED)
    c.text_block(tx, y + 40, headline, 3, INK, tw, line_gap=5)
    # deck starts below the two-line headline
    c.text_block(tx, y + 40 + 2 * (7 * 3 + 5) + 10, deck, 2, INK, tw,
                 line_gap=5)


def draw_grid(c):
    y0, y1 = 468, 940
    pw, ph, gap = 496, 228, 16
    draw_panel(c, 0, y0, pw, ph, draw_chart_art, "ECONOMY - WALL STREET",
               "S&P 500 ENTERS CORRECTION",
               "AI STOCKS PLUNGE ON FRIDAY; DOW ALSO IN CORRECTION.")
    draw_panel(c, pw + gap, y0, pw, ph, draw_flags_art,
               "POLITICS - BRUSSELS",
               "UK AND EU SIGN DEALS",
               "FOOD TRADE, CARBON MARKETS, YOUTH MOBILITY.")
    draw_panel(c, 0, y0 + ph + gap, pw, ph, draw_riyadh_art,
               "MIDDLE EAST - RIYADH",
               "MISSILES OVER RIYADH",
               "SAUDI COALITION INTERCEPTS HOUTHI ATTACK.")
    draw_panel(c, pw + gap, y0 + ph + gap, pw, ph, draw_cricket_art,
               "SPORT - CRICKET",
               "INDIA V NEW ZEALAND",
               "RAHUL, PADIKKAL STEADY INDIA ON DAY THREE.")


def draw_ticker(c):
    y0 = 956
    c.fill_rect(0, y0, W, H - y0, NAVY)
    c.text(16, y0 + 8, "ALSO TODAY:", 2, RED)
    c.text(16, y0 + 27,
           "PANCREATIC-CANCER PILL HAILED A BREAKTHROUGH", 2, WHITE)
    c.text(16, y0 + 46,
           "ASTEROID 2026 WA1 FLIES PAST EARTH - YOUTH PROTESTS IN EUROPE",
           2, WHITE)


def build():
    c = Canvas(W, H, PAPER)
    draw_masthead(c)
    draw_lead(c)
    draw_grid(c)
    draw_ticker(c)
    return png_bytes(c)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = build()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
